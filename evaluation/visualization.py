import pandas as pd
from algbench import read_as_pandas
import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns

def runtime_statistics(dfs, save_path=None, figsize=(4.5, 0.9 * 4.5), backends=["CP-SAT", "MIP", "SAT[Glucose4]"], instance_types=['srpg_iso_aligned_mc'], max_instance_size=1619, round_precision=25, hue="backend", title="", hue_order=None, ax=None, legend=True):
    # filter data set
    dfs = dfs[(dfs["backend"].isin(backends)) & (dfs["type"].isin(instance_types)) & (dfs["size"] <= max_instance_size)]
    dfs["size_rounded"] = dfs["size"].apply(lambda x: (round_precision * round(x / round_precision)))
    
    if ax is None:
        plt.figure(figsize=figsize)
        ax = plt.gca()

    sns.lineplot(
        data=dfs,
        x="size_rounded",
        y="runtime",
        hue=hue,
        ci=None,
        hue_order=hue_order,
        ax=ax
    )
    ax.set_xlabel('average size', fontsize=10, color='black')
    ax.set_ylabel('runtime (s)', fontsize=10, color='black')
    ax.tick_params(axis='x', colors='black')
    ax.tick_params(axis='y', colors='black')
    ax.set_title(title, fontsize=10)
    if not legend:
        ax.legend().set_visible(False)
    else:
        ax.legend(title=None, fontsize=7)
    if save_path:
        plt.savefig(save_path, bbox_inches='tight')

def add_type(df):
    conditions = [
        df['instance'].str.startswith('simple'),
        df['instance'].str.startswith('general'),
        df['instance'].str.startswith('srpg_iso_aligned_mc'),
        df['instance'].str.startswith('srpg_iso_aligned'),
        df['instance'].str.startswith('srpg_iso_mc')
    ]
    choices = ['scot_simple','scot_general','srpg_iso_aligned_mc','srpg_iso_aligned','srpg_iso_mc']
    choices_2 = ['scots_hole_free', 'scots', 'orthogonal', 'orthogonal_hole_free', 'orthogonal']
    choices_3 = ['scots', 'scots', 'orthogonal', 'orthogonal', 'orthogonal']
    df['type'] = np.select(conditions, choices, default='srpg_iso')
    df['type_class'] = np.select(conditions, choices_2, default='orthogonal_hole_free')
    df['general_class'] = np.select(conditions, choices_3, default='orthogonal')
    return df

if __name__ == "__main__":

    df = read_as_pandas(
    "/Users/kaiko/Desktop/evaluation/disp_agp_benchmark",
    lambda result: {
        "instance": result["parameters"]["args"]["instance_name"],
        "size": result["parameters"]["args"]["size"],
        "backend": result["parameters"]["args"]["alg_params"]["backend"],
        "obj": result["result"]["dispersion_distance"],
        "runtime": result["runtime"],
        },
    )

    df = add_type(df)

    plt.style.use('ggplot')
    plt.rcParams['axes.facecolor'] = '#EAEDEF'
    plt.rcParams['font.family'] = 'serif'
    plt.rcParams['text.usetex'] = True
    plt.rcParams['font.size'] = 10

    ROUNDING = 40

    # Compare SAT[Glucose4], CP-SAT, and MIP on random orthogonal polygons
    df2 = df.copy()
    df2["backend"] = df2["backend"].replace({
        "MIP": "MIP[Gurobi]"
    })

    runtime_statistics(df2, 
                       instance_types=["srpg_iso_aligned_mc", "srpg_iso_aligned","srpg_iso_mc", "srpg_iso"], 
                       backends=["CP-SAT", "MIP[Gurobi]", "SAT[Glucose4]"], 
                       max_instance_size=1000, 
                       round_precision=ROUNDING, 
                       hue_order=["CP-SAT", "MIP[Gurobi]", "SAT[Glucose4]"],
                       save_path="plots/compare_cpsat_sat_mip.pdf",
                       figsize=(2.2, 0.9 * 2.2)
                       )
    
    # Compare SAT[Glucose4], CP-SAT, and MIP on random scots
    df2 = df.copy()
    df2["backend"] = df2["backend"].replace({
        "MIP": "MIP[Gurobi]"
    })

    runtime_statistics(df2, 
                       instance_types=["scot_simple", "scot_general"], 
                       backends=["CP-SAT", "MIP[Gurobi]", "SAT[Glucose4]"], 
                       max_instance_size=1000, 
                       round_precision=ROUNDING, 
                       hue_order=["CP-SAT", "MIP[Gurobi]", "SAT[Glucose4]"],
                       save_path="plots/compare_scots_cpsat_sat_mip.pdf",
                       figsize=(2.2, 0.9 * 2.2)
                       )
    
    # Compare different SAT solvers on random orthogonal polygons
    df2 = df.copy()
    df2["backend"] = df2["backend"].replace({
        "SAT[Cadical153]": "Cadical153", 
        "SAT[Glucose4]": "Glucose4", 
        "SAT[Gluecard4]": "Gluecard4", 
        "SAT[Lingeling]": "Lingeling", 
        "SAT[MapleCM]": "MapleCM", 
        "SAT[Minisat22]": "Minisat22"
    })

    runtime_statistics(df2, 
                       instance_types=["srpg_iso_aligned_mc", "srpg_iso_aligned","srpg_iso_mc", "srpg_iso"], 
                       backends=["Cadical153", "Glucose4", "Gluecard4", "Lingeling", "MapleCM", "Minisat22"], 
                       max_instance_size=1600, 
                       round_precision=ROUNDING, 
                       hue_order=["Cadical153", "Glucose4", "Gluecard4", "Lingeling", "MapleCM", "Minisat22"],
                       save_path="plots/compare_different_sat.pdf",
                       figsize=(2.2, 0.9 * 2.2)
                       )

    fig, axes = plt.subplots(1, 3, figsize=(3*1.8,3* 0.5 * 1.4), sharey=False)
    """# Compare SAT[Glucose4] performance for SCOTs and general orthogonal polygons (with and without holes, respectively)
    runtime_statistics(df,
                       ax=axes[2], 
                       instance_types=["srpg_iso_aligned_mc", "srpg_iso_aligned","srpg_iso_mc", "srpg_iso", "scot_simple", "scot_general"], 
                       backends=["SAT[Glucose4]"], 
                       max_instance_size=1600, 
                       round_precision=ROUNDING, 
                       hue="type_class", 
                       title="SAT[Glucose4]", 
                       hue_order=["orthogonal", "orthogonal_hole_free", "scots", "scots_hole_free"],
                       figsize=(1.4, 0.9 * 1.4),
                       legend=False
                       )

    # Compare CP-SAT performance for SCOTs and general orthogonal polygons (with and without holes, respectively)
    runtime_statistics(df, 
                       ax=axes[0],  
                       instance_types=["srpg_iso_aligned_mc", "srpg_iso_aligned","srpg_iso_mc", "srpg_iso", "scot_simple", "scot_general"], 
                       backends=["CP-SAT"], 
                       max_instance_size=1000, 
                       round_precision=ROUNDING, 
                       hue="type_class", 
                       title="CP-SAT", 
                       hue_order=["orthogonal", "orthogonal_hole_free", "scots", "scots_hole_free"],
                       figsize=(1.4, 0.9 * 1.4),
                       legend=False
                       )

    # Compare MIP performance for SCOTs and general orthogonal polygons (with and without holes, respectively)
    df2 = df.copy()
    df2["backend"] = df2["backend"].replace({
        "MIP": "MIP[Gurobi]"
    })
    runtime_statistics(df2, 
                       ax=axes[1],  
                       instance_types=["srpg_iso_aligned_mc", "srpg_iso_aligned","srpg_iso_mc", "srpg_iso", "scot_simple", "scot_general"], 
                       backends=["MIP[Gurobi]"], 
                       max_instance_size=1000, 
                       round_precision=ROUNDING, 
                       hue="type_class", 
                       title="MIP[Gurobi]", 
                       hue_order=["orthogonal", "orthogonal_hole_free", "scots", "scots_hole_free"],
                       figsize=(1.4, 0.9 * 1.4),
                       legend=False
                       )"""
    
    # Compare CP-SAT performance for SCOTs and orthogonal polygons
    runtime_statistics(df, 
                       ax=axes[0],
                       instance_types=["srpg_iso_aligned_mc", "srpg_iso_aligned","srpg_iso_mc", "srpg_iso", "scot_simple", "scot_general"], 
                       backends=["CP-SAT"], 
                       max_instance_size=1000, 
                       round_precision=ROUNDING, 
                       hue="general_class", 
                       title="CP-SAT", 
                       hue_order=["orthogonal", "scots"],
                       figsize=(1.4, 0.9 * 1.4),
                       legend=False
                       )
    
    # Compare MIP performance for SCOTs and orthogonal polygons
    df2 = df.copy()
    df2["backend"] = df2["backend"].replace({
        "MIP": "MIP[Gurobi]"
    })
    runtime_statistics(df2, 
                       ax=axes[1],
                       instance_types=["srpg_iso_aligned_mc", "srpg_iso_aligned","srpg_iso_mc", "srpg_iso", "scot_simple", "scot_general"], 
                       backends=["MIP[Gurobi]"], 
                       max_instance_size=1000, 
                       round_precision=ROUNDING, 
                       hue="general_class", 
                       title="MIP[Gurobi]", 
                       hue_order=["orthogonal", "scots"],
                       figsize=(1.4, 0.9 * 1.4),
                       legend=False
                       )
    
    # Compare SAT performance for SCOTs and orthogonal polygons
    runtime_statistics(df, 
                       ax=axes[2],
                       instance_types=["srpg_iso_aligned_mc", "srpg_iso_aligned","srpg_iso_mc", "srpg_iso", "scot_simple", "scot_general"], 
                       backends=["SAT[Glucose4]"], 
                       max_instance_size=1600, 
                       round_precision=ROUNDING, 
                       hue="general_class", 
                       title="SAT[Glucose4]", 
                       hue_order=["orthogonal", "scots"],
                       figsize=(1.4, 0.9 * 1.4),
                       legend=False
                       )


fig.tight_layout()
handles, labels = axes[0].get_legend_handles_labels()
fig.legend(handles, labels, loc='center', bbox_to_anchor=(0.5, -0.05), ncol=len(handles), fontsize=7)
plt.savefig("plots/all_backends_merged.pdf", bbox_inches='tight')
plt.close()