# SOLAR-MICRO-GRID-DISPATCH-PLANNER
This project focuses on a microgrid that is run by both batteries and solar energy at a health center. Daily, the energy drawn from solar panels (x) and batteries (y) must satisfy two demand constraints: 
- 3x + 2y = D1 (daytime load, kWh)                        
- 4x + y = D2 (critical-equipment load, kWh)
-  This code was edited with the aid of CODEX, an Artificial Intelligence powered tool.
### IMPLEMENTATION
- Using object oriented programming in python,  a Microgrid class that holds the coefficient matrix and exposes solve day(d1, d2) was created. 
- Two input modes were created: an interactive input and 30 random days of demand
- Physically infeasible days were detected and flagged.
- A statistics report was made to identify the more volatile option between solar and battery usage.
- Daily and monthly costs of using solar and batteries were computed and plotted.
### FINDINGS, LIMITATIONS AND RECOMMENDATIONS
- The determinant is -5 so it has a unique solution for the solar and battery contributions. With a condition number of 5.82, the solar and battery allocations are to a smaller extent sensitive to battery and solar changes.
- Both the vectorized call and python loop of the generated  CSV produced the same results. The vectorized approach took 0.429716 seconds and was faster than the loop that took 6.200580seconds.
- Four infeasible days were discovered and using non negative least squares, a combination of solar and battery that comes closest to satisfying the demand equations was used in each instance.
- The solar and battery mean, variance and standard deviation were as follows: Solar (28.21, 7.89, 2.81) Battery( 9.44, 39.03, 6.25) respectively. Battery is more volatile since it has a larger variance and standard deviation compared to the solar.
- Given that solar is at UGX 150/kWh and battery at UGX 450/kWh , the total solar cost is UGX 126,940.38, total battery cost is UGX 127,382.49 and  the total monthly cost is UGX 254,322.88.

