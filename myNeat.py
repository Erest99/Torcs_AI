import os.path

import neat.config


def run(config_path):
    config = neat.config.Config(
        neat.DefaultGenome,
        neat.DefaultReproduction,
        neat.DefaultSpeciesSet,
        neat.DefaultStagnation,
        config_path
    )

    pop = neat.Population(config)
    '''run fitness function 50 times'''
    pop.run(eval_genomes, 50)

    if __name__ == '__main__':
        local_dir = os.path.dirname(__file__)
        config_path = os.path.joim(local_dir, 'config.txt')
        run(config_path)