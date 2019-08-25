# given data
list_of_campaigns = ["TV","SEO","Adwords","Facebook"]
roi_values = {"TV":9,"SEO":14,"Adwords":10,"Facebook":5}
penetration_values = {"TV":2.5,"SEO":2.1,"Adwords":0.9,"Facebook":3}
budget = 1000000
viewer_count = 1300000

# pulp
import pulp
model = pulp.LpProblem(name="ad_revenue_optimization",sense = pulp.LpMaximize)

# Indexes >> Campaigns to Evaluate
model.campaign = list_of_campaigns

# Parameters >> Data Available
# Defining this may not be necessary
model.total_budget = budget
model.total_viewers = viewer_count
model.roi = roi_values
model.penetration = penetration_values

# Variables >> Budget Allocations
model.allocation = {c:pulp.LpVariable(name="z_"+str(c), lowBound = 0, cat='Continuous')
                        for c in model.campaign}
# Ref : https://www.coin-or.org/PuLP/pulp.html#pulp.LpVariable

# Constraints >> As provided in seq
model.primary_spend_equation = model.addConstraint(
        pulp.LpConstraint(
            e = model.allocation["SEO"] + model.allocation["Adwords"],
            sense = pulp.LpConstraintLE,
            name = "primary spend limit",
            rhs = 0.6*model.total_budget))

model.facebook_limit_equation = model.addConstraint(
        pulp.LpConstraint(
            e = model.allocation["Facebook"],
            sense = pulp.LpConstraintLE,
            name = "facebook_limit",
            rhs = 0.2*model.total_budget))

model.minimum_tv_spend_equation = model.addConstraint(
        pulp.LpConstraint(
            e = model.allocation["TV"],
            sense = pulp.LpConstraintGE,
            name = "minimum_tv_spend",
            rhs = 200000))

model.social_media_commitment_equation = model.addConstraint(
        pulp.LpConstraint(
            e = model.allocation["Facebook"],
            sense = pulp.LpConstraintGE,
            name = "social_media_commitment",
            rhs = 80000))

model.spend_ratio_strategy_equation = model.addConstraint(
        pulp.LpConstraint(
            e = model.allocation["Adwords"],
            sense = pulp.LpConstraintLE,
            name = "spend_ratio_strategy",
            rhs = 3*model.allocation["SEO"]))

model.seo_cc_contract_equation_1 = model.addConstraint(
        pulp.LpConstraint(
            e = model.allocation["SEO"],
            sense = pulp.LpConstraintGE,
            name = "seo_cc_contract_lower",
            rhs = 60000))

model.seo_cc_contract_equation_2 = model.addConstraint(
        pulp.LpConstraint(
            e = model.allocation["SEO"],
            sense = pulp.LpConstraintLE,
            name = "seo_cc_contract_higher",
            rhs = 220000))

model.target_market_reach = model.addConstraint(
        pulp.LpConstraint(
            e = pulp.lpSum(model.allocation[c]*model.penetration[c] for c in model.campaign),
            sense = pulp.LpConstraintGE,
            name = "market_reach_achievement",
            rhs = model.total_viewers))

model.total_budget_equation = model.addConstraint(
        pulp.LpConstraint(
            e = pulp.lpSum(model.allocation[c] for c in model.campaign),
            sense = pulp.LpConstraintLE,
            name = "total_budget_allocation",
            rhs = model.total_budget))

# Objective Function >>
objective = pulp.lpSum(model.allocation[c]*(model.roi[c]/100) for c in model.campaign)
model.setObjective(objective)

#----------------------------------- Method : pulp.solve -------------------------------------------------------------
model.solve(pulp.solvers.COIN(msg=True))
