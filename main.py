# !/usr/bin/env python
'''
Message communication and parser created on Apr 4, 2012
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
from pynput.keyboard import Key, Controller as KeyController
import pywinauto
import subprocess
import pyautogui
import win32gui


def eval_genomes(genomes, config):
    global ge, nets
    i = -1
    ge = []
    nets = []
    print(str(i + 2))
    counter = 0

    for genome_id, genome in genomes:
        ge.append(genome)
        net = neat.nn.FeedForwardNetwork.create(genome, config)
        nets.append(net)
        genome.fitness = 0


        # Configure the argument parser
        parser = argparse.ArgumentParser(description='Python client to connect to the TORCS SCRC server.')

        # parser.add_argument('--host', action='store', dest='host_ip', default='localhost',
        #                     help='Host IP address (default: localhost)')
        parser.add_argument('--host', action='store', dest='host_ip', default='localhost',
                            help='Host IP address (default: 172.17.0.0)')
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

        # app = pywinauto.Application(backend='uia').connect(title='wtorcs.exe', timeout=1)
        # window = app["wtorcs.exe"]
        # window.set_focus()
        # window.type_keys('{ENTER}', with_spaces=True)
        # window.type_keys('{ENTER}', with_spaces=True)
        # app.disconnect()

        win32gui.SetActiveWindow(desktop_window_handle)
        pyautogui.press('enter')
        time.sleep(1)
        pyautogui.press('enter')
        # runDocker()


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
    #p = neat.Checkpointer.restore_checkpoint('neat-checkpoint-1000')
    #p = neat.Checkpointer.restore_checkpoint('neat-checkpoint-750')
    #p = neat.Checkpointer.restore_checkpoint('neat-checkpoint-500')
    #p = neat.Checkpointer.restore_checkpoint('neat-checkpoint-250')
    p = neat.Population(config)
    p.add_reporter(neat.StdOutReporter(True))

    stats = neat.StatisticsReporter()
    p.add_reporter(stats)
    p.add_reporter(neat.Checkpointer(1))

    print("checkpoint 2")

    counter = 0
    best = p.run(eval_genomes, 251)
    with open("best.pickle", "wb") as f:
        pickle.dump(best, f)


def run_torcs(start):
    win32gui.SetActiveWindow(desktop_window_handle)
    print('opening TORCS')
    if (start):
        subprocess.Popen(['start_torcs.bat'], shell=True)
    time.sleep(10)
    time.sleep(15)
    print('setting TORCS')
    pyautogui.press('enter')
    time.sleep(1)
    pyautogui.press('enter')
    time.sleep(1)
    pyautogui.press('down')
    time.sleep(1)
    pyautogui.press('enter')
    time.sleep(1)
    pyautogui.press('enter')
    time.sleep(1)
    pyautogui.press('enter')
    time.sleep(1)
    pyautogui.press('down')
    time.sleep(1)
    pyautogui.press('right')
    time.sleep(1)
    pyautogui.press('delete')
    time.sleep(1)
    pyautogui.press('down')
    time.sleep(1)
    pyautogui.press('enter')
    time.sleep(1)
    pyautogui.press('up')
    time.sleep(1)
    pyautogui.press('enter')


def runDocker():

    # Replace this with the full path to the directory where you extracted the TORCS game data
    torcs_data_dir = r"C:\Program Files (x86)\torcs"

    # Replace this with the full path to the race configuration XML file you downloaded
    race_config_file = r"C:\Program Files (x86)\torcs\config\raceman\quickrace.xml"

    # Build the Docker command to run the TORCS server
    docker_command = ["docker", "run", "-p", "3001:3001", "-v", f"{torcs_data_dir}:/root/.torcs", "-v",
                      f"{race_config_file}:/torcs_server_config/race_config.xml", "tkpgamification/torcs_server", "-l",
                      "1", "-r", "1", "-c", "/torcs_server_config/race_config.xml"]

    # Use the 'runas' command to run the Docker command as admin
    runas_command = ["runas", "/user:Administrator"] + docker_command

    try:
        output = subprocess.check_output(runas_command, stderr=subprocess.STDOUT)
    except subprocess.CalledProcessError as e:
        output = e.output
        print(f"Error running Docker command: {e}")
    print(output.decode())


if __name__ == '__main__':
    # mouse = MouseController()
    # keyboard = KeyController()

    desktop_window_handle = win32gui.FindWindow("Progman", "Program Manager")
    local_dir = os.path.dirname(__file__)
    config_path = os.path.join(local_dir, 'config.txt')

    config = neat.config.Config(
        neat.DefaultGenome,
        neat.DefaultReproduction,
        neat.DefaultSpeciesSet,
        neat.DefaultStagnation,
        config_path)
    value = input("NoStart(0)/Train(1)/Test(2)?\n")
    if value == "1":
        app = run_torcs(True)
        run_neat(config)
    elif value == "0":
        runDocker()
        run_neat(config)
    else:
        # app = run_torcs(False)
        testai()
