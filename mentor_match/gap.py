#!/usr/bin/env python

from gurobipy import GRB, Model

# The equivalent variables from Wikipedia: https://en.wikipedia.org/wiki/Generalized_assignment_problem
#   costs   := w
#   profits := p
#   budgets := t
# GAP: [[costs]], [budgets], [[profits]], bool -> objval, [[assignment]]
# Solve the generalized assignment problem using Gurobi
def GAP(costs, budgets, profits, allAgentsGetTask=False):
    a = costs
    b = budgets
    c = profits

    model = Model('GAP')
    model.modelSense = GRB.MAXIMIZE
    model.setParam('OutputFlag', False) # turns off solver chatter

    # 1. Create decision variables
    # x[i][j] = 1 if i is assigned to j
    x = []
    for i in range(len(c)):
        x_i = []
        for j in c[i]:
            x_i.append(model.addVar(vtype=GRB.BINARY))
        x.append(x_i)

    # We have to update the model so it knows about new variables
    model.update()

    # 2. Add constraints
    # sum j: x_ij = 1 for all i
    for x_i in x:
        model.addConstr(sum(x_i) == 1)

    # sum i: a_ij * x_ij <= b[j] for all j
    for j in range(len(b)):
        model.addConstr(sum(a[i][j] * x[i][j] for i in range(len(x))) <= b[j])
        if allAgentsGetTask:
            model.addConstr(sum(x[i][j] for i in range(len(x))) >= 1)

    # 3. Set objective
    # max sum i,j: c_ij * x_ij
    model.setObjective(
        sum(
            sum(c_ij * x_ij for c_ij, x_ij in zip(c_i, x_i))
            for c_i, x_i in zip(c, x)
        )
    )

    # 4. Solve the model
    model.optimize()

    # 5. Pull objective and variable values out of model
    assignment = []
    for x_i in x:
        assignment.append([1 if x_ij.x >= 0.5 else 0 for x_ij in x_i])
    return (model.objVal, assignment)

if __name__ == "__main__":
    # Sample problem 1
    budgets = [15, 15, 15]
    profits = [
        [ 6, 10,  1],
        [12, 12,  5],
        [15,  4,  3],
        [10,  3,  9],
        [ 8,  9,  5]
    ]
    costs = [
        [ 5,  7,  2],
        [14,  8,  7],
        [10,  6, 12],
        [ 8,  4, 15],
        [ 6, 12,  5]
    ]
    (objval, assignment) = GAP(costs, budgets, profits)
    # Manually verified this assignment is best
    # Obj value: 43 (expected)
    print 'Problem 1: '
    print 'objective =', objval
    print 'x = ['
    for x_i in assignment:
        print '   ', x_i
    print ']'
    assert objval == 43

    # Sample problem 2
    # http://support.sas.com/documentation/cdl/en/ormpug/65554/HTML/default/viewer.htm#ormpug_decomp_examples02.htm
    # Verified that the objective value returned from the Gurobi solver (563)
    # matches the value on the webpage.
    profits = [
        [25, 23, 20, 16, 19, 22, 20, 16, 15, 22, 15, 21, 20, 23, 20, 22, 19, 25, 25, 24,
        21, 17, 23, 17],
        [16, 19, 22, 22, 19, 23, 17, 24, 15, 24, 18, 19, 20, 24, 25, 25, 19, 24, 18, 21,
        16, 25, 15, 20],
        [20, 18, 23, 23, 23, 17, 19, 16, 24, 24, 17, 23, 19, 22, 23, 25, 23, 18, 19, 24,
        20, 17, 23, 23],
        [16, 16, 15, 23, 15, 15, 25, 22, 17, 20, 19, 16, 17, 17, 20, 17, 17, 18, 16, 18,
        15, 25, 22, 17],
        [17, 23, 21, 20, 24, 22, 25, 17, 22, 20, 16, 22, 21, 23, 24, 15, 22, 25, 18, 19,
        19, 17, 22, 23],
        [24, 21, 23, 17, 21, 19, 19, 17, 18, 24, 15, 15, 17, 18, 15, 24, 19, 21, 23, 24,
        17, 20, 16, 21],
        [18, 21, 22, 23, 22, 15, 18, 15, 21, 22, 15, 23, 21, 25, 25, 23, 20, 16, 25, 17,
        15, 15, 18, 16],
        [19, 24, 18, 17, 21, 18, 24, 25, 18, 23, 21, 15, 24, 23, 18, 18, 23, 23, 16, 20,
        20, 19, 25, 21]
    ]
    profits = map(list, zip(*profits)) # transpose it

    costs = [
        [8, 18, 22, 5, 11, 11, 22, 11, 17, 22, 11, 20, 13, 13,  7, 22, 15, 22, 24,  8,  8,
        24, 18,  8],
        [24, 14, 11, 15, 24,  8, 10, 15, 19, 25,  6, 13, 10, 25, 19, 24, 13, 12,  5, 18,
        10, 24,  8,  5],
        [22, 22, 21, 22, 13, 16, 21,  5, 25, 13, 12,  9, 24,  6, 22, 24, 11, 21, 11, 14,
        12, 10, 20,  6],
        [13,  8, 19, 12, 19, 18, 10, 21,  5,  9, 11,  9, 22,  8, 12, 13,  9, 25, 19, 24, 22,
        6, 19, 14],
        [25, 16, 13,  5, 11,  8,  7,  8, 25, 20, 24, 20, 11,  6, 10, 10,  6, 22, 10, 10,
        13, 21,  5, 19],
        [19, 19,  5, 11, 22, 24, 18, 11,  6, 13, 24, 24, 22,  6, 22,  5, 14,  6, 16, 11,
        6, 8, 18, 10],
        [24, 10,  9, 10,  6, 15,  7, 13, 20,  8,  7,  9, 24,  9, 21,  9, 11, 19, 10,  5,
        23, 20,  5, 21],
        [6,  9,  9,  5, 12, 10, 16, 15, 19, 18, 20, 18, 16, 21, 11, 12, 22, 16, 21, 25,
        7, 14, 16, 10]
    ]
    costs = map(list, zip(*costs)) # transpose it

    budgets = [36, 35, 38, 34, 32, 34, 31, 34]

    (objval, assignment) = GAP(costs, budgets, profits)
    print 'Problem 2: '
    print 'objective =', objval
    print 'x = ['
    for x_i in assignment:
        print '   ', x_i
    print ']'
    assert objval == 563


