# given data
list_of_campaigns = ["TV","SEO","Adwords","Facebook"]
roi_values = {"TV":9,"SEO":14,"Adwords":10,"Facebook":5}
penetration_values = {"TV":2.5,"SEO":2.1,"Adwords":0.9,"Facebook":3}
budget = 1000000
viewer_count = 1300000

# pyomo concrete model
from pyomo.environ import *
model = ConcreteModel()

# Indexes >> Campaigns to Evaluate
model.campaign = Set(initialize = list_of_campaigns)

# Parameters >> Data Available
model.roi = Param(model.campaign, initialize = roi_values)
model.penetration = Param(model.campaign, initialize =penetration_values)
model.total_budget = Param(initialize = budget)
model.total_viewers = Param(initialize = viewer_count)

# Variables >> Budget Allocations
model.allocation = Var(model.campaign, within= NonNegativeReals)

# Constraints >> As provided in seq
def primary_spend_limit(model):
	return model.allocation["SEO"] + model.allocation["Adwords"] <= 0.6*model.total_budget
model.primary_spend_equation = Constraint(rule=primary_spend_limit)

def facebook_limit(model):
	return model.allocation["Facebook"] <= 0.2*model.total_budget
model.facebook_limit_equation = Constraint(rule = facebook_limit)

def minimum_tv_spend(model):
	return model.allocation["TV"] >= 200000
model.minimum_tv_spend_equation = Constraint(rule=minimum_tv_spend)

def social_media_commitment(model):
	return model.allocation["Facebook"] >= 80000
model.social_media_commitment_equation = Constraint(rule = social_media_commitment)

def spend_ratio_strategy(model):
	return model.allocation["Adwords"] <= 3*model.allocation["SEO"]
model.spend_ratio_strategy_equation = Constraint(rule = spend_ratio_strategy)

def seo_cc_contract_lower(model):
	return model.allocation["SEO"] >= 60000
model.seo_cc_contract_equation_1 = Constraint(rule = seo_cc_contract_lower)

def seo_cc_contract_higher(model):
	return model.allocation["SEO"] <= 220000
model.seo_cc_contract_equation_2 = Constraint(rule = seo_cc_contract_higher)

def market_reach_achievement(model):
	return sum(model.allocation[c]*model.penetration[c] for c in model.campaign) >= model.total_viewers
model.target_market_reach = Constraint(rule=market_reach_achievement)

def total_budget_allocation(model):
	return sum(model.allocation[c] for c in model.campaign) <= model.total_budget
model.total_budget_equation = Constraint(rule = total_budget_allocation)

# Objective Function >> Achieve all of these while maximum roi
model.objective = Objective(expr = sum(model.allocation[c]*(model.roi[c]/100) for c in model.campaign),sense=maximize)

#----------------------------------- Method : pyomo.solve -------------------------------------------------------------
# >>>> cbc/glpk (present as one of the environment variables)

opt = SolverFactory('cbc',solver_io = 'lp')
# opt.options["sec"] = 180
# opt.options['threads'] = 2
results = opt.solve(model, tee= True)
model.solutions.store_to(results)
# print (results)
results.write()
