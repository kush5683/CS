def selection(population):
    """
    selection function
    uses roulette wheel selection to select parents
    with probability proportional to fitness
    """
    selection_population = []
    total_fitness = 0
    for b in population:
        total_fitness += b.fitness()
    # print(total_fitness)
    for b in population:
        if total_fitness == 0:
            b.set_selection_probability(1/len(population))
        else:
            b.set_selection_probability((b.fitness() + 10) / total_fitness)
        for p in range(int(b.selection_probability * 100)):
            selection_population.append(b)

    return selection_population


def elitism(population):
    """
    elitism function keeps top 3 performers
    """
    number_to_keep = 3
    p = population.copy()
    p.sort(key=lambda x: x.fitness(), reverse=True)
    return p[:number_to_keep]


def culling(population):
    """
    culling function removes set percentage of the population
    """
    percent_to_remove = 0.33
    p = population.copy()
    p.sort(key=lambda x: x.fitness(), reverse=True)
    bottom_25_percent = int(len(p) * percent_to_remove)
    return p[:-bottom_25_percent]
