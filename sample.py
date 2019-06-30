"""

"""
from pyomo.environ import *

model = pyomo.environ.ConcreteModel()

model.market = pyomo.environ.Set(initialize=['market'])

model.ask_price = pyomo.environ.Param(model.market, initialize={'market' : 12})
model.bid_price = pyomo.environ.Param(model.market, initialize={'market' : 10})
model.ask_liquidity = pyomo.environ.Param(model.market, initialize={'market' : 100})
model.bid_liquidity = pyomo.environ.Param(model.market, initialize={'market' : 100})

model.VOLUME_BUY = pyomo.environ.Var(model.market, within = pyomo.environ.NonNegativeReals)
model.VOLUME_SELL = pyomo.environ.Var(model.market, within = pyomo.environ.NonNegativeReals)

def max_buy(model, market):
    return model.VOLUME_BUY[market] <= model.ask_liquidity[market]
model.max_buy_equation = pyomo.environ.Constraint(model.market, rule=max_buy)

def max_sell(model, market):
    return model.VOLUME_SELL[market] <= model.bid_liquidity[market]
model.max_sell_equation = pyomo.environ.Constraint(model.market, rule=max_sell)

def objective_component1(model):
    return sum(model.VOLUME_BUY[market] * model.ask_price[market] for market in model.market)
model.obj_component1 = pyomo.environ.Expression(rule=objective_component1)

def objective_component2(model):
    return - sum(model.VOLUME_SELL[market] * model.bid_price[market] for market in model.market)
model.obj_component2 = pyomo.environ.Expression(rule=objective_component2)
model.objective = pyomo.environ.Objective(expr=model.obj_component1 + model.obj_component2, sense=-1)

#----------------------------------- Method : pyomo.solve -------------------------------------------------------------
# >>>> 1. OpenSource : cbc/glpk (present as one of the environment variables)

opt = SolverFactory('cbc',solver_io = 'lp')
# opt.options["sec"] = 180
# opt.options['threads'] = 2
results = opt.solve(model, tee= True)
model.solutions.store_to(results)
print (results)

# >>>> 2. NEOS Server
# Note : Solver Log while solving cannot be retrived
# Available Options of Solver with NEOS : https://neos-server.org/neos/solvers/index.html
# Dependencies(python3):pyro4, suds, openopt

solver_manager = SolverManagerFactory('neos')
opt = SolverFactory('cplex', solver_io = 'lp')
results = solver_manager.solve(model, opt=opt)
model.solutions.store_to(results)
print (results)

# >>>> 3. docplexcloud
# key = #DOCPLEX API KEY (get from docloud website)
# base_url = #DOCPLEX URL (get from docloud website)
# Dependencies : docloud (pip install docloud)

import json
import glob
import pandas
from docloud.job import JobClient
client = JobClient(base_url,key)
model.write("temp.lp", io_options={"symbolic_solver_labels": True})
# with open("temp.lp") as lpfile:
#     resp = client.execute(input=lpfile,output=None,load_solution = True)
file = glob.glob("temp.lp")
resp = client.execute(input=file,output=None,load_solution = True)
solution = json.loads(resp.solution.decode("utf-8"))
#os.remove(file)
for i,k in solution['CPLEXSolution']['header'].items():
    print(i,':',k)
results = pandas.DataFrame(solution['CPLEXSolution']['variables']).filter(items= ['index','name','value','status'])
print (results)


# >>>> 4. GUROBI

## TBD

exit()
