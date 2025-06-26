from disp_agp_solver import solve, get_instance_from_graphml_xz
from algbench import Benchmark
import slurminade
import os
import re
from pathlib import Path

slurminade.set_dispatch_limit(10000)

def get_name_from_filepath(filepath):
    f = str(filepath)
    name = f.split(f"{os.sep}")[-1][:-11]
    return name

def extract_wall_time(text):
    match = re.search(r'walltime:\s*([\d.]+)', text)
    if match:
        print("Yes")
        return float(match.group(1))
    else:
        return None

benchmark = Benchmark(Path.home() / "dagp_build_evaluation/disp_agp_benchmark_model")

slurminade.update_default_configuration(
    partition = "alg",
    constraint = "alggen05",
    exclusive = True,
    mail_user = "kobbe@ibr.cs.tu-bs.de",
    mail_type = "FAIL"
)

@slurminade.slurmify()
def load_instance_and_run(path, instance_name, alg_params):
    instance = get_instance_from_graphml_xz(path)
    size = instance.num_positions()
    if not alg_params["backend"].startswith("SAT") and size > 1000: return
    
    def eval_solver(instance_name, size, alg_params, _instance):
        solution, objective, upper_bound, stats = solve(_instance, **alg_params)
        return {
            "time_compute_witnesses": stats['time_compute_vispolys'] + stats['time_compute_shadow_witnesses'],
            "time_solve": stats["gurobi"]["runtime"] if alg_params["backend"] == "MIP" else extract_wall_time(stats['solve_stats'][0]['CP-SAT'])
        }

    benchmark.add(eval_solver, instance_name, size, alg_params, instance)

@slurminade.slurmify(mail_type="ALL")
def compress():
    benchmark.compress()

@slurminade.node_setup
def configure_grb_license_path():
    import socket

    if "alg" not in socket.gethostname():
        return

    grb_license_path = Path.home() / ".gurobi" / socket.gethostname() / "gurobi.lic"
    import os

    os.environ["GRB_LICENSE_FILE"] = str(grb_license_path)

    if not grb_license_path.exists():
        msg = "Gurobi License File does not exist."
        raise RuntimeError(msg)

alg_params = [
    {"backend": "MIP"},
    {"backend": "CP-SAT"},
]

if __name__ == "__main__":
    with slurminade.JobBundling(max_size=50):
        for root, _, files in os.walk(Path.home() / "solving-dispersive-agp/experiments/instances"):
            for file in files:
                for conf in alg_params:
                    if not str(file).endswith(".graphml.xz"): continue
                    print(file)
                    path = root + "/" + file
                    name = get_name_from_filepath(path)
                    load_instance_and_run.distribute(path, name, conf)
                
        slurminade.join()
        compress.distribute()
