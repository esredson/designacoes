from constraint import Problem, AllDifferentConstraint, MinConflictsSolver
import numpy as np

class CSP:

    def __init(self, funcional, agenda):
        self._pool = [funcional.funcoes[k] for k in funcional.funcoes.keys()]
        self._tam_array = len(agenda.datas_validas)

    def executar(self):
        pass

    @property
    def solucao(self):
        return self._solucao

    @property
    def tempo_execucao(self):
        return self._tempo_execucao

problem = Problem(solver=MinConflictsSolver())
pool = [
    ['aug', 'ed', 'gei', 'igo', 'paul', 'rob', 'serg', 'vic'],
    ['aug', 'ed', 'gei', 'igo', 'paul', 'rob', 'serg', 'vic'],
    ['aug', 'ed', 'gei', 'igo', 'rob', 'serg', 'vic', 'raf'],
    ['deb', 'gei', 'raf']
]
num_cols = len(pool)
num_rows = 8
for i in range(num_cols):
    for j in range(num_rows):
        problem.addVariable(f"{i}-{j}", pool[i])

def calculate_mean_distance_with_reference(array, reference_values):
    distances = []

    for ref_val in reference_values:
        indices = [i for i, val in enumerate(array) if val == ref_val]
        qtd_indices = len(indices)
        if qtd_indices == 0:
            distances.append(0)
        elif qtd_indices == 1:
            distances.append(len(reference_values))
        else:
            distances.append(np.mean(np.diff(indices))) 
            
    return np.mean(distances)/float(len(reference_values))

def constraint2(i):
    def my_constraint2(*tupla):
        return calculate_mean_distance_with_reference(tupla, pool[i]) == 1.0
    return my_constraint2

for j in range(num_rows):
    problem.addConstraint(AllDifferentConstraint(),tuple(f"{i}-{j}" for i in range(num_cols)))

for i in range(num_cols):
    problem.addConstraint(constraint2(i), tuple(f"{i}-{j}" for j in range(num_rows)))

print(problem.getSolution())