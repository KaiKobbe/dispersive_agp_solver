from disp_agp_solver import solve, get_instance_from_graphml_xz
from algbench import Benchmark
import slurminade
import os
from pathlib import Path

slurminade.set_dispatch_limit(10000)

def get_name_from_filepath(filepath):
    f = str(filepath)
    name = f.split(f"{os.sep}")[-1][:-11]
    return name

benchmark = Benchmark(Path.home() / "solving-dispersive-agp/experiments/evaluation/disp_agp_benchmark")

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
        solution, objective, upper_bound = solve(_instance, **alg_params)
        return {
            "dispersion_distance": objective
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
    {"backend": "SAT[Cadical103]"},
    {"backend": "SAT[Cadical153]"},
    {"backend": "SAT[Gluecard3]"},
    {"backend": "SAT[Gluecard4]"},
    {"backend": "SAT[Glucose3]"},
    {"backend": "SAT[Glucose4]"},
    {"backend": "SAT[Lingeling]"},
    {"backend": "SAT[MapleChrono]"},
    {"backend": "SAT[MapleCM]"},
    {"backend": "SAT[Maplesat]"},
    {"backend": "SAT[Mergesat3]"},
    {"backend": "SAT[Minicard]"},
    {"backend": "SAT[Minisat22]"},
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
