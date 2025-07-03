# Experimental Evaluation

We evaluated the solvers for different types of orthogonal polygons.
On the one hand, we evaluated 745 random orthogonal polygons from the [Salzburg Database](https://sbgdb.cs.sbg.ac.at). 
Moreover, we randomly generated 1599 polygons which we refer to as office-like.

Roughly speaking, office-like polygons are meant to mimic real-world floor plans consisting of rectangular rooms that are connected by rectangular corridors. 
These polygons were first introduced by [Cruz and Tomas] which refer to them as SCOTs.
For more detailed definitions we refer to ... or ...
The below figure depicts two random ortohonal polygons and two random office-like polygons, each type once with and once without holes.

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
The below plots provide an intuition on the performance of our solvers.
A more complete analysis can be found in the paper.
Our collected experimental data can be found [here]().


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

