# !/usr/bin/env python
'''
Created on Apr 4, 2012
@author: lanquarden
'''
import sys
import argparse
import socket
import time
import pickle

import driver
import math
import sys
import neat
import os
from pynput.mouse import Button, Controller as MouseController


def eval_genomes(genomes, config):
    global ge, nets
    i = -1
    ge = []
    nets = []
    print(str(i+2))

    for genome_id, genome in genomes:
        ge.append(genome)
        net = neat.nn.FeedForwardNetwork.create(genome, config)
        nets.append(net)
        genome.fitness = 0

        # Configure the argument parser
        parser = argparse.ArgumentParser(description='Python client to connect to the TORCS SCRC server.')

        parser.add_argument('--host', action='store', dest='host_ip', default='localhost',
                            help='Host IP address (default: localhost)')
        parser.add_argument('--port', action='store', type=int, dest='host_port', default=3001,
                            help='Host port number (default: 3001)')
        parser.add_argument('--id', action='store', dest='id', default='SCR',
                            help='Bot ID (default: SCR)')
        parser.add_argument('--maxEpisodes', action='store', dest='max_episodes', type=int, default=1,
                            help='Maximum number of learning episodes (default: 1)')
        parser.add_argument('--maxSteps', action='store', dest='max_steps', type=int, default=0,
                            help='Maximum number of steps (default: 0)')
        parser.add_argument('--track', action='store', dest='track', default=None,
                            help='Name of the track')
        parser.add_argument('--stage', action='store', dest='stage', type=int, default=3,
                            help='Stage (0 - Warm-Up, 1 - Qualifying, 2 - Race, 3 - Unknown)')

        arguments = parser.parse_args()

        # Print summary
        '''
        print('Connecting to server host ip:', arguments.host_ip, '@ port:', arguments.host_portprint)
        '''
        print('Bot ID:', arguments.id)
        print('Maximum episodes:', arguments.max_episodes)
        print('Maximum steps:', arguments.max_steps)
        print('Track:', arguments.track)
        print('Stage:', arguments.stage)

        '*********************************************'

        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        except socket.error as msg:
            print('Could not make a socket.')

            sys.exit(-1)

        # one second timeout
        sock.settimeout(1.0)

        shutdownClient = False
        curEpisode = 0

        verbose = False

        d = driver.Driver(arguments.stage)

        while not shutdownClient:
            while True:
                go = True
                print('Sending id to server: ', arguments.id)
                buf = arguments.id + d.init()
                print('Sending init string to server:', buf)

                try:
                    sock.sendto(str.encode(buf), (arguments.host_ip, arguments.host_port))
                except socket.error as msg:
                    print("Failed to send data...Exiting...")

                    sys.exit(-1)

                try:
                    buf, addr = sock.recvfrom(1000)
                except socket.error as msg:
                    # TODO Await and try again
                    print("didn't get response from server...")
                    go = False;

                if go:
                    if buf.find(str.encode('***identified***')) >= 0:
                        print('Received: ', buf)
                        break

            currentStep = 0

            while True:
                # wait for an answer from server
                buf = None
                try:
                    buf, addr = sock.recvfrom(1000)
                except socket.error as msg:
                    print("didn't get response from server...")

                if verbose:
                    print('Received: ', buf)

                if buf is not None and buf.find(str.encode('***shutdown***')) >= 0:
                    d.onShutDown()
                    shutdownClient = True
                    print('Client Shutdown')
                    break

                if buf is not None and buf.find(str.encode('***restart***')) >= 0:
                    d.onRestart()
                    print('Client Restart')
                    break

                currentStep += 1
                if currentStep != arguments.max_steps:
                    if buf is not None:
                        buf = d.drive(buf, ge, nets, i, config)
                else:
                    buf = '(meta 1)'

                if verbose:
                    print('Sending: ', buf)

                if buf is not None:
                    try:
                        sock.sendto(str.encode(buf), (arguments.host_ip, arguments.host_port))
                    except socket.error as msg:
                        print("Failed to send data...Exiting...")

                        sys.exit(-1)

            curEpisode += 1

            if curEpisode == arguments.max_episodes:
                shutdownClient = True

        sock.close()

        mouse = MouseController()
        time.sleep(1)

        mouse.position = (320, 460)
        mouse.press(Button.left)
        mouse.release(Button.left)

        mouse.position = (320, 120)
        mouse.press(Button.left)
        mouse.release(Button.left)

def testai():

    with open("best.pickle", "rb") as f:
        best = pickle.load(f)
    best_net = neat.nn.FeedForwardNetwork.create(best, config)

    # Configure the argument parser
    parser = argparse.ArgumentParser(description='Python client to connect to the TORCS SCRC server.')

    parser.add_argument('--host', action='store', dest='host_ip', default='localhost',
                        help='Host IP address (default: localhost)')
    parser.add_argument('--port', action='store', type=int, dest='host_port', default=3001,
                        help='Host port number (default: 3001)')
    parser.add_argument('--id', action='store', dest='id', default='SCR1',
                        help='Bot ID (default: SCR1)')
    parser.add_argument('--maxEpisodes', action='store', dest='max_episodes', type=int, default=1,
                        help='Maximum number of learning episodes (default: 1)')
    parser.add_argument('--maxSteps', action='store', dest='max_steps', type=int, default=0,
                        help='Maximum number of steps (default: 0)')
    parser.add_argument('--track', action='store', dest='track', default=None,
                        help='Name of the track')
    parser.add_argument('--stage', action='store', dest='stage', type=int, default=3,
                        help='Stage (0 - Warm-Up, 1 - Qualifying, 2 - Race, 3 - Unknown)')

    arguments = parser.parse_args()

    # Print summary
    '''
    print('Connecting to server host ip:', arguments.host_ip, '@ port:', arguments.host_portprint)
    '''
    print('Bot ID:', arguments.id)
    print('Maximum episodes:', arguments.max_episodes)
    print('Maximum steps:', arguments.max_steps)
    print('Track:', arguments.track)
    print('Stage:', arguments.stage)

    '*********************************************'

    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    except socket.error as msg:
        print('Could not make a socket.')

        sys.exit(-1)

    # one second timeout
    sock.settimeout(1.0)

    shutdownClient = False
    curEpisode = 0

    verbose = False

    d = driver.Driver(arguments.stage)

    while not shutdownClient:
        while True:
            go = True
            print('Sending id to server: ', arguments.id)
            buf = arguments.id + d.init()
            print('Sending init string to server:', buf)

            try:
                sock.sendto(str.encode(buf), (arguments.host_ip, arguments.host_port))
            except socket.error as msg:
                print("Failed to send data...Exiting...")

                sys.exit(-1)

            try:
                buf, addr = sock.recvfrom(1000)
            except socket.error as msg:
                # TODO Await and try again
                print("didn't get response from server...")
                go = False;

            if go:
                if buf.find(str.encode('***identified***')) >= 0:
                    print('Received: ', buf)
                    break

        currentStep = 0

        while True:
            # wait for an answer from server
            buf = None
            try:
                buf, addr = sock.recvfrom(1000)
            except socket.error as msg:
                print("didn't get response from server...")

            if verbose:
                print('Received: ', buf)

            if buf is not None and buf.find(str.encode('***shutdown***')) >= 0:
                d.onShutDown()
                shutdownClient = True
                print('Client Shutdown')
                break

            if buf is not None and buf.find(str.encode('***restart***')) >= 0:
                d.onRestart()
                print('Client Restart')
                break

            currentStep += 1
            if currentStep != arguments.max_steps:
                if buf is not None:
                    buf = d.testdrive(buf, best_net)
            else:
                buf = '(meta 1)'

            if verbose:
                print('Sending: ', buf)

            if buf is not None:
                try:
                    sock.sendto(str.encode(buf), (arguments.host_ip, arguments.host_port))
                except socket.error as msg:
                    print("Failed to send data...Exiting...")

                    sys.exit(-1)

        curEpisode += 1

        if curEpisode == arguments.max_episodes:
            shutdownClient = True

    sock.close()


def run_neat(config):
    # load from  checkpoint
    #p = neat.Checkpointer.restore_checkpoint('neat-checkpoint-206')
    p = neat.Population(config)
    p.add_reporter(neat.StdOutReporter(True))
    stats = neat.StatisticsReporter()
    p.add_reporter(stats)
    p.add_reporter(neat.Checkpointer(1))

    best = p.run(eval_genomes, 2)
    with open("best.pickle", "wb") as f:
        pickle.dump(best, f)


if __name__ == '__main__':
    local_dir = os.path.dirname(__file__)
    config_path = os.path.join(local_dir, 'config.txt')

    config = neat.config.Config(
        neat.DefaultGenome,
        neat.DefaultReproduction,
        neat.DefaultSpeciesSet,
        neat.DefaultStagnation,
        config_path)
    value = input("Train/Test?\n")
    if value == "Train":
        run_neat(config)
    else:
        testai()
