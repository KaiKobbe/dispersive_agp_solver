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

benchmark = Benchmark(Path.home() / "dagp_sat_phases_evaluation/disp_agp_benchmark_sat")

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
        num_unsat, num_sat, time_unsat, time_sat = 0, 0, 0, 0
        statistics =  stats['iteration_statistics'][0]['solver']['solver']['solve_statistics']
        for d in statistics:
            if d['status'] == False:
                num_unsat += 1
                time_unsat += d['time']
                continue
            num_sat += 1
            time_sat += d['time']
        return {
            "number_sat_probes": stats['iteration_statistics'][0]['solver']['solver']['solve_calls'],
            "number_sat_solves": num_sat,
            "number_unsat_solves": num_unsat,
            "time_compute_witnesses": stats['time_compute_vispolys'] + stats['time_compute_shadow_witnesses'],
            "time_compute_vispolys": stats['time_compute_vispolys'],
            "time_compute_shadow_witnesses": stats['time_compute_shadow_witnesses'],
            "time_unsat_solves": time_unsat,
            "time_sat_solves": time_sat,
            "time_compute_distances_from_graph": stats["time_compute_distances_from_graph"],
            "time_build_distance_graph": stats["time_build_distance_graph"],
            "total_model_build_time": stats["iteration_statistics"][0]["solver"]["total_build_time"]
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
    {"backend": "SAT"},
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