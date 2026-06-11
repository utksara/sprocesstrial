## Centaurus CMD script generation instructions

For each of these sections, generate a command file (.cmd) which can be run by the Sprocess module of Sentaurus based on the provided instructions. For each scenario, create a separate folder with a .cmd file and a results folder to store all generated files.

1. Simple anonymous particle etching (etching with a fictitious particle that removes the etch boundary at a certain rate).

- Surface preparation
    - Prepare a 2D surface with a horizontal boundary (along the x-axis); let's say the width of the boundary is "w".
    - Particles are coming from the top onto that surface with normal incidence.
    - Apply uniform meshing to the surface with size = 0.01 * w.
    
- Monte Carlo scheme to simulate particles
    - Divide the top surface into N = 10 parts (N should be a modifiable variable).
    - For each division, calculate the probability density using a Gaussian distribution function, and separately calculate a random number between 0 and 1 with a precision of up to two decimal places. If the random number is less than the probability distribution value of that point, a particle is assumed to be present there; otherwise, it is not.
    - If a particle exists, get its x-coordinate value and calculate the y-coordinate of the current state of the 2D surface.
    - At these points on the surface, the surface should deform; essentially, use the meshing to calculate a circular deformation with a radius of 0.05 * w.
- After all N divisions are processed, re-mesh the surface.

- Repeat the process up to m = 20 times, with m being a variable value.


In the 'daily_automation_script.sh' file, write the corresponding Sprocess script for each scenario above, one by one. Terminate the script if it takes longer than 2 minutes to run. After that, write a simple shell script code to:
- git add -A
- git commit -m "sentaurus_run_{date}_{time}"
- git push