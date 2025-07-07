# Experimental Evaluation

We analyzed solver performance across different types of orthogonal polygons.
To this end, we evaluated 745 random orthogonal polygons from the [Salzburg Database](https://sbgdb.cs.sbg.ac.at) and 1599 randomly generated polygons, which we refer to as office-like.

Roughly speaking, office-like polygons are designed to mimic real-world floor plans composed of rectangular rooms connected by rectangular corridors.
These polygons were first introduced by [Cruz and Tomás](https://link.springer.com/chapter/10.1007/978-3-031-20624-5_43), who referred to them as SCOTs.
A more detailed definition can be found in their work via the link above or in our paper.

The figures below show two randomly generated orthogonal polygons and two randomly generated office-like polygons—each type once with holes and once without.

<table align="center">
  <tr>
    <td align="center" valign="middle">
      <img src="https://github.com/KaiKobbe/dispersive_agp_solver/blob/main/figures/png/exemplary_instances/srpg_iso_aligned_mc0000201.png?raw=true" height="110">
    </td>
    <td align="center" valign="middle">
      <img src="https://github.com/KaiKobbe/dispersive_agp_solver/blob/main/figures/png/exemplary_instances/srpg_iso0000201.png?raw=true" height="110">
    </td>
    <td align="center" valign="middle">
      <img src="https://github.com/KaiKobbe/dispersive_agp_solver/blob/main/figures/png/exemplary_instances/general_200_4.png?raw=true" height="110">
    </td>
    <td align="center" valign="middle">
      <img src="https://github.com/KaiKobbe/dispersive_agp_solver/blob/main/figures/png/exemplary_instances/simple_200_4.png?raw=true" height="110">
    </td>
  </tr>
</table>

All instances were executed once for each solver on an Ubuntu Linux workstation equipped with an AMD Ryzen 9 7900 processor and 96 GB of RAM. 
The implementation was written in Python 3.12.8 using PySAT 1.8dev14, OR-Tools 9.11.4210, and Gurobi 12.0.1. 
Geometric computations were performed in C++ using CGAL 5.6.1 and integrated via PyBind11.
The plots below provide a visual overview of how the solvers perform.
For a more detailed analysis, please refer to the paper.
The experimental data is available [here](https://github.com/KaiKobbe/dispersive_agp_solver/tree/main/evaluation).


<table align="center">
  <tr>
    <td align="center" valign="middle">
      <img src="https://github.com/KaiKobbe/dispersive_agp_solver/blob/main/figures/png/runtime_plots/compare_different_sat.png?raw=true" height="170">
    </td>
    <td align="center" valign="middle">
      <img src="https://github.com/KaiKobbe/dispersive_agp_solver/blob/main/figures/png/runtime_plots/compare_cpsat_sat_mip.png?raw=true" height="170">
    </td>
  </tr>
</table>

