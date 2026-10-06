#!/usr/bin/env python
# coding: utf-8

# In[2]:


#import libraries
import numpy as np 
import pandas as pd
import statistics
import timeit
import matplotlib.pyplot as plt
from scipy.linalg import solve
from scipy.optimize import nnls


# In[3]:


"""Creating the Microgrid class. Each day, the energy drawn from solar panels (x) and batteries (y) must satisfy two demand constraints:
3x + 2y = D1      (daytime load, kWh)
4x +  y = D2      (critical-equipment load, kWh)"""
class MicroGrid:
    def __init__(self):
        self.A = np.array([[3, 2],[4, 1]], dtype=float)
        # Computing the determinant
        self.determinant = np.linalg.det(self.A)
        # Computing the condition number
        self.condition_number = np.linalg.cond(self.A)

    def check_system(self):
        print("Coefficient matrix:")
        print(self.A)
        print(f"\nDeterminant: {self.determinant:.4f}")
        print(f"Condition number: {self.condition_number:.4f}")
        if np.isclose(self.determinant, 0):
            print("The system is singular and cannot be solved uniquely.")
        else:
            print("The system has a unique mathematical solution.")

    def solve_day(self, d1, d2):
        b = np.array([d1, d2], dtype=float)
        # Solve Ax = b
        solution = solve(self.A, b)
        solar = solution[0]
        battery = solution[1]
        return solar, battery


# In[4]:


#testing
grid = MicroGrid()
grid.check_system()


# In[5]:


# interactive input() with robust validation (reject nonnumeric, negative and empty values, and re-prompt)
def get_positive_demand(prompt):
    while True:
        value = input(prompt).strip()
        if value == "":
            print("Please enter a number.")
            continue
        try:
            value = float(value)
        except ValueError:
            print("Please enter a number.")
            continue

        if value < 0:
            print("Please enter a positive number ")
            continue
        return value


# In[6]:


#an interactive function
def interactive_day(grid):
    d1 = get_positive_demand("Please enter the daytime load D1 (kWh): ")
    d2 = get_positive_demand("Please enter the critical-equipment load D2 (kWh): ")
    solar, battery = grid.solve_day(d1, d2)
    print("\nResults")
    print(f"Solar usage: {solar:.2f} kWh")
    print(f"Battery usage: {battery:.2f} kWh")
    if solar < 0 or battery < 0:
        print("This  combination is physically infeasible.")
    else:
        print("The solution is physically feasible.")


# In[7]:


"""loading 30 days of demand from a CSV file. Generate the CSV yourself with a seeded random 
generator: realistic values with a weekly pattern and some noise"""
rng = np.random.default_rng(42)
days = np.arange(1, 31)
d1_values = []
d2_values = []
for day in days:
    # Monday = 0,...Sunday = 6
    weekday = (day - 1) % 7
    # Weekly demand pattern
    if weekday < 5:
        weekly_effect = 5
    else:
        weekly_effect = -5

    d1 = 100 + weekly_effect + rng.normal(0, 8)
    d2 = 120 + weekly_effect + rng.normal(0, 10)

    d1_values.append(d1)
    d2_values.append(d2)

df = pd.DataFrame({"Day": days,"D1": d1_values,"D2": d2_values})
df.to_csv("microgrid_30_days.csv", index=False)
df.head()


# In[8]:


data = pd.read_csv("microgrid_30_days.csv")

print(data.head())
print("\nNumber of days:", len(data))


# In[9]:


"""Solve all 30 days with scipy.linalg.solve, first in a Python loop and then in a single 
vectorised call (pass a 2×30 right-hand side). Time both approaches with timeit and 
comment on the difference."""
def solve_with_loop(grid, data):
    results = []
    for _, row in data.iterrows():
        d1 = row["D1"]
        d2 = row["D2"]
        solution = solve(grid.A,np.array([d1, d2]))
        results.append(solution)

    return np.array(results)
loop_results = solve_with_loop(grid, data)
print(loop_results[:5])
results = data.copy()
results["Solar"] = loop_results[:, 0]
results["Battery"] = loop_results[:, 1]
results.head()


# In[10]:


#vectorised bit
B = np.vstack([data["D1"].to_numpy(),data["D2"].to_numpy()])
print(B.shape)
vectorised_results = solve(grid.A, B)
print(vectorised_results.shape)
results["Solar_vectorised"] = vectorised_results[0]
results["Battery_vectorised"] = vectorised_results[1]

print(results.head())


# In[11]:


#time the loop and vectorised approaches
loop_time = timeit.timeit(lambda: solve_with_loop(grid, data),number=1000)
print(f"Loop time: {loop_time:.6f} seconds")
def solve_vectorised(grid, data):
    B = np.vstack([data["D1"].to_numpy(),data["D2"].to_numpy()])
    return solve(grid.A, B)
vectorised_time = timeit.timeit(lambda: solve_vectorised(grid, data),number=1000)
print(f"Vectorised time: {vectorised_time:.6f} seconds")


# In[12]:


"""Detect and flag physically infeasible days (negative x or y). Propose and 
implement a sensible handling strategy, for example clipping plus a report, or 
switching to a non-negative least-squares solver (scipy.optimize.nnls)."""
results["Infeasible"] = ((results["Solar"] < 0) |(results["Battery"] < 0))
print(results[results["Infeasible"]])
print("Number of infeasible days:",results["Infeasible"].sum())


# In[13]:


#handling infeasible days
def solve_with_nnls(grid, d1, d2):
    b = np.array([d1, d2], dtype=float)
    solution, residual = nnls(grid.A, b)
    return solution[0], solution[1]
nnls_results = []

for _, row in data.iterrows():
        solar, battery = solve_with_nnls(grid,row["D1"],row["D2"])
        nnls_results.append([solar, battery])
nnls_results = np.array(nnls_results)
results["Solar_NNLS"] = nnls_results[:, 0]
results["Battery_NNLS"] = nnls_results[:, 1]


# In[14]:


#compare solutions
print(results[results["Infeasible"] ][["Day","D1","D2","Solar","Battery","Solar_NNLS","Battery_NNLS"]])
#vectorised solution
B = np.vstack([data["D1"].values,data["D2"].values])
print(B.shape)
vectorised_results = solve(grid.A, B)
print(vectorised_results.shape)
"""Final solar usage/batterry usage:Use the normal mathematical solution when feasible 
and NNLS solution when the mathematical solution is infeasible."""
results["Solar_Final"] = np.where(results["Infeasible"],results["Solar_NNLS"],results["Solar"])
results["Battery_Final"] = np.where(results["Infeasible"],results["Battery_NNLS"],results["Battery"])


# In[15]:


#descriptive statistics
solar = results["Solar_Final"].tolist()
battery = results["Battery_Final"].tolist()
solar_mean = statistics.mean(solar)
solar_variance = statistics.variance(solar)
solar_std = statistics.stdev(solar)

battery_mean = statistics.mean(battery)
battery_variance = statistics.variance(battery)
battery_std = statistics.stdev(battery)
print("SOLAR")
print(f"Mean: {solar_mean:.2f}")
print(f"Variance: {solar_variance:.2f}")
print(f"Standard deviation: {solar_std:.2f}")

print("\nBATTERY")
print(f"Mean: {battery_mean:.2f}")
print(f"Variance: {battery_variance:.2f}")
print(f"Standard deviation: {battery_std:.2f}")


# In[16]:


#Cost model: given solar at UGX 150/kWh and battery at UGX 450/kWh (illustrative), compute the daily and monthly energy cost.
SOLAR_COST = 150
BATTERY_COST = 450
results["Solar_Cost"] = (results["Solar_Final"] * SOLAR_COST)
results["Battery_Cost"] = (results["Battery_Final"] * BATTERY_COST)
results["Daily_Cost"] = (results["Solar_Cost"] +results["Battery_Cost"])
print(results[["Day","Solar_Final","Battery_Final","Daily_Cost"]])
#monthly ennergy cost
monthly_cost = results["Daily_Cost"].sum()
print( f"30-day energy cost: UGX {monthly_cost:,.2f}")
#total cost from each cost
total_solar_cost = results["Solar_Cost"].sum()
total_battery_cost = results["Battery_Cost"].sum()
print(f"Total solar cost: UGX {total_solar_cost:,.2f}")
print(f"Total battery cost: UGX {total_battery_cost:,.2f}")
print(f"Total monthly cost: UGX "f"{monthly_cost:,.2f}")


# In[17]:


#Plot daily solar vs battery usage as a stacked bar chart, with a second axis showing daily cost.
fig, ax1 = plt.subplots(figsize=(14, 7))
days = results["Day"]
# Stacked energy usage
ax1.bar(days,results["Solar_Final"],label="Solar")
ax1.bar(days,results["Battery_Final"],bottom=results["Solar_Final"],label="Battery")

ax1.set_xlabel("Day")
ax1.set_ylabel("Energy usage (kWh)")
ax1.set_title("Daily Solar and Battery Usage with Energy Cost")
ax1.legend(loc="upper left")
# Second axis
ax2 = ax1.twinx()
ax2.plot(days,results["Daily_Cost"],marker="o",label="Daily Cost",color="black")
ax2.set_ylabel("Daily Energy Cost (UGX)")
ax2.legend(loc="upper right")
plt.tight_layout()
plt.show()


# In[ ]:




