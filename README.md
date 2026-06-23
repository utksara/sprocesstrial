# Sentaurus Etching Simulation.


## **Imporant** - General instructions for working on any git repository
1) Craeting a branch - always create a branch with a this syntax \<yourname/abbrevation\>_\<purpose\>. For example if I want to add parsing feature, I will name my branch as 
utk_parsing. 
2) Rebasing - Since the main repository is continously evolving, daily rebase your current working
with the main branch, that will make filing PR a lot easier.
3) Filling a merge/pull request - Make sure you current branch is first rebased with the target (main) branch and then file the PR.
4) While filing a new branch, also make sure to update the [task section](## Tasks) section below. No need to update the current state section.


## How to run the script
- since sentaurus is running in a remote machine, all scripts have to be run via sentaurus_automation.py using command ```poetry run python3 sentaurus_automation.py```
- the changes related to which sentauris scripts (.cmd files) to run have to implemented in remote_task.sh since sentaurus_automation.py ultimately copies the script to remote machine and runs it
-------------------------------------------------------------------------------------

## Current state
- OxideMaskedHighAspectRatioEtch.cmd is working file
- Simple case of etching with top photoresist layer, oxide layer and silicon substrate
- Etch rate pre-defined
- Flow rate of SF6, Bias power, Pressure, etch time are specified

## Tasks

Update this section each time a change is made

### Task 1 : 
- [x] Modify the paramters of the OxideMaskedHighAspectRatioEtch.cmd etching, like SF6 flow rate,  Bias power, Pressure and list all of their combinations in a yaml or json file. 
- [x] For each combination, create different versions of OxideMaskedHighAspectRatioEtch.cmd file and run them to see if anything changes in the figure and save the results in csv file ( with value of each paramters changed and corresponding .cmd, .tdr and .log file)
- [x] With constant value of pressure, try different etch rates which range within 0.2 to 5 times the existing etching rate and add the same data in the csv files


### Task 2: 
- [x] Determine etch rate just with Flow rate of SF6, Bias power, Pressure without having to specify it explicitly and save it in the csv file as before
- [x] Go through the OxideMaskedHighAspectRatioEtch_withFlux.cmd and see what is common and different between this file and OxideMaskedHighAspectRatioEtch.cmd  (for example here the silicon etch rate is specified, while in the previous file a rate parameters is specified in the etch section is specified)
- [x] vary the etching time and etchign cycles (try upto 20 etching cycles) and record the data in the csv file

### Task 2.5:
- [x] In the current result csv files for task 1 and task 2, go through .log file of each row, parse the relevent information from it which includes 
    - Substrate Geometry (X, Y, Z dimensions)
    - Oxide thickness deposited (Oxide Deposition Before Etch)
    - Mask opening Geometry 
    - etch type, requested depth and material etched
    - Photoresist thickness
    - Deposited vs Etched Thickness 
    - etch depth calculated calculated using Deposited - Etched Thickness
    - Nodes and Volumes after etching
    - Smallest Region After Etch and it's volume
- [x] add these news columns to same csv files of task 1 and task 2

### Task 3:
- [ ] In the current code there is no way to measure how much depth and width has been achieved, use
.tdr and .log files find a way to extract depth and other dimension in the etching profile
- [ ] In the csv file worked before, record the depth and bottom CD, top CD and mid CD in the etching profile

### Task 4:
- [ ] Now also add the deposition simulation with C4F8 after each etching cycle, keep the time of deposition 1/3rd to 1/4th of the etching time 
- [ ] Collect etching and deposition data for upto 100 cycles and time for 7 seconds for etchign and 2 seconds for deposition and save them in the csv file


## Simulation scenarios
1) Simple anonymous particle etching (etching with a fictitious particle that removes the etch boundary at a certain rate).
2) Individual chemical species simulation (for just the etching part).
3) Simple particle distribution simulation where we just measure values of particle distribution at different points in space.
4) Simple simulation of removal of the etching surface.
5) Uniform etching simulation.