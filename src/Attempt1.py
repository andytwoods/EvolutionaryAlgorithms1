import random

from deap import base
from deap import creator
from deap import tools


class FitnessMax(base.Fitness):
    def __init__(self,  *args, **kargs):
        self.weights = (1.0,)
        super(FitnessMax, self).__init__(*args, **kargs)

class Individual(list):
    def __init__(self,  *args, **kargs):
        self.fitness = FitnessMax()
        super(Individual, self).__init__(*args, **kargs)



class Evolution(object):


    def __init__(self):

        self.toolbox = base.Toolbox()

        self.setup()

    def setup(self):

        # Attribute generator
        self.toolbox.register("attr_bool", random.randint, 0, 1)
        # Structure initializers
        self.toolbox.register("individual", tools.initRepeat, Individual, self.toolbox.attr_bool, 100)
        self.toolbox.register("population", tools.initRepeat, list, self.toolbox.individual)


        # Operator registering
        self.toolbox.register("mate", tools.cxTwoPoint)
        self.toolbox.register("mutate", tools.mutFlipBit, indpb=0.05)
        self.toolbox.register("select", tools.selTournament, tournsize=3)

        random.seed(64)

        pop = self.toolbox.population(n=300)

        print("Start of evolution")

        # Evaluate the entire population
        self.evaluate(pop, self.begin_evolving)

    def begin_evolving(self, pop):

        CXPB, MUTPB, NGEN = 0.5, 0.2, 4

        # Begin the evolution
        for g in range(NGEN):
            self.run_generation(CXPB, MUTPB, g, pop)

        self.report(pop)


    def report(self, pop):
        print("-- End of (successful) evolution --")
        best_ind = tools.selBest(pop, 1)[0]
        print("Best individual is %s, %s" % (best_ind, best_ind.fitness.values))


    def run_generation(self, CXPB, MUTPB, g, pop):
        print("-- Generation %i --" % g)
        # Select the next generation individuals
        offspring = self.toolbox.select(pop, len(pop))
        # Clone the selected individuals
        offspring = list(map(self.toolbox.clone, offspring))
        # Apply crossover and mutation on the offspring
        for child1, child2 in zip(offspring[::2], offspring[1::2]):
            if random.random() < CXPB:
                self.toolbox.mate(child1, child2)
                del child1.fitness.values
                del child2.fitness.values
        for mutant in offspring:
            if random.random() < MUTPB:
                self.toolbox.mutate(mutant)
                del mutant.fitness.values

        # Evaluate the individuals with an invalid fitness
        invalid_ind = [ind for ind in offspring if not ind.fitness.valid]
        self.evaluate(invalid_ind)
        # The population is entirely replaced by the offspring
        pop[:] = offspring
        # Gather all the fitnesses in one list and print the stats
        fits = [ind.fitness.values[0] for ind in pop]
        length = len(pop)
        mean = sum(fits) / length
        sum2 = sum(x * x for x in fits)
        std = abs(sum2 / length - mean ** 2) ** 0.5
        print("  Min %s" % min(fits))
        print("  Max %s" % max(fits))
        print("  Avg %s" % mean)
        print("  Std %s" % std)



    def evaluate(self, children, callback = None):

        #pool.add_many(children)

        for ind in children:
            ind.fitness.values = self.evalOneMax(ind)



        print("  Evaluated %i individuals" % len(children))

        if callback is not None:
            callback(children)


    def evalOneMax(self, individual):
        return sum(individual),

debug = Evolution()


