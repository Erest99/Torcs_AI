import math

import msgParser
import carState
import carControl
import pdb, traceback, sys

import neat


class Driver(object):
    '''
    A driver object for the SCRC
    '''

    def __init__(self, stage):
        '''Constructor'''
        self.WARM_UP = 0
        self.QUALIFYING = 1
        self.RACE = 2
        self.UNKNOWN = 3
        self.stage = stage

        self.parser = msgParser.MsgParser()

        self.state = carState.CarState()

        self.control = carControl.CarControl()

        self.steer_lock = 0.785398
        self.max_speed = 120
        self.prev_rpm = 3000
        '''none -> nebude řadit dolu'''

    def init(self):
        '''Return init string with rangefinder angles'''
        self.angles = [0 for x in range(19)]

        for i in range(5):
            self.angles[i] = -90 + i * 15
            self.angles[18 - i] = 90 - i * 15

        for i in range(5, 9):
            self.angles[i] = -20 + (i - 5) * 5
            self.angles[18 - i] = 20 - (i - 5) * 5

        return self.parser.stringify({'init': self.angles})

    def drive(self, msg, ge, nets, i, config):
        self.state.setFromMsg(msg)

        ge[i].fitness = self.state.distRaced - 30 * self.state.curLapTime
        if ge[i].fitness < -500:
            ge[i].fitness = -100000
            self.control.setMeta(1)

        if float(self.state.wheelSpinVel[0]) >= 0:
            wheel1 = float(1 / (self.state.wheelSpinVel[0] + 1))
        else:
            wheel1 = - float(1/(abs(self.state.wheelSpinVel[0]) + 1))

        if float(self.state.wheelSpinVel[1]) >= 0:
            wheel2 = float(1 / (self.state.wheelSpinVel[1] + 1))
        else:
            wheel2 = - float(1 / (abs(self.state.wheelSpinVel[1]) + 1))

        if float(self.state.wheelSpinVel[2]) >= 0:
            wheel3 = float(1 / (self.state.wheelSpinVel[2] + 1))
        else:
            wheel3 = - float(1 / (abs(self.state.wheelSpinVel[2]) + 1))

        if float(self.state.wheelSpinVel[3]) >= 0:
            wheel4 = float(1 / (self.state.wheelSpinVel[3] + 1))
        else:
            wheel4 = - float(1 / (abs(self.state.wheelSpinVel[3]) + 1))


        data = [
            float(self.state.angle / math.pi),
            float(1/(self.state.damage+1)),
            float(1/(self.state.fuel+1)),
            self.state.gear/6,
            # float(self.state.opponents[0]) / 200,
            # float(self.state.opponents[1]) / 200,
            # float(self.state.opponents[2]) / 200,
            # float(self.state.opponents[3]) / 200,
            # float(self.state.opponents[4]) / 200,
            # float(self.state.opponents[5]) / 200,
            # float(self.state.opponents[6]) / 200,
            # float(self.state.opponents[7]) / 200,
            # float(self.state.opponents[8]) / 200,
            # float(self.state.opponents[9]) / 200,
            # float(self.state.opponents[10]) / 200,
            # float(self.state.opponents[11]) / 200,
            # float(self.state.opponents[12]) / 200,
            # float(self.state.opponents[13]) / 200,
            # float(self.state.opponents[14]) / 200,
            # float(self.state.opponents[15]) / 200,
            # float(self.state.opponents[16]) / 200,
            # float(self.state.opponents[17]) / 200,
            # float(self.state.opponents[18]) / 200,
            # float(self.state.opponents[19]) / 200,
            # float(self.state.opponents[20]) / 200,
            # float(self.state.opponents[21]) / 200,
            # float(self.state.opponents[22]) / 200,
            # float(self.state.opponents[23]) / 200,
            # float(self.state.opponents[24]) / 200,
            # float(self.state.opponents[25]) / 200,
            # float(self.state.opponents[26]) / 200,
            # float(self.state.opponents[27]) / 200,
            # float(self.state.opponents[28]) / 200,
            # float(self.state.opponents[29]) / 200,
            # float(self.state.opponents[30]) / 200,
            # float(self.state.opponents[31]) / 200,
            # float(self.state.opponents[32]) / 200,
            # float(self.state.opponents[33]) / 200,
            # float(self.state.opponents[34]) / 200,
            # float(self.state.opponents[35]) / 200,
            # self.state.opponents,
            # self.state.racePos,
            float(1/(self.state.rpm+1)),
            float(self.state.speedX/1000),
            float(self.state.speedY/1000),
            float(self.state.speedZ/1000),
            float(self.state.track[0]) / 200,
            float(self.state.track[1]) / 200,
            float(self.state.track[2]) / 200,
            float(self.state.track[3]) / 200,
            float(self.state.track[4]) / 200,
            float(self.state.track[5]) / 200,
            float(self.state.track[6]) / 200,
            float(self.state.track[7]) / 200,
            float(self.state.track[8]) / 200,
            float(self.state.track[9]) / 200,
            float(self.state.track[10]) / 200,
            float(self.state.track[11]) / 200,
            float(self.state.track[12]) / 200,
            float(self.state.track[13]) / 200,
            float(self.state.track[14]) / 200,
            float(self.state.track[15]) / 200,
            float(self.state.track[16]) / 200,
            float(self.state.track[17]) / 200,
            float(self.state.track[18]) / 200,
            float(self.state.trackPos/5),
            wheel1,
            wheel2,
            wheel3,
            wheel4,
            float(self.state.z/100),
        ]
        output = nets[i].activate(data)
        # normalize = [abs(output[1]), abs(output[2])]
        # maximum = max(normalize)
        output[1] = 1/abs(output[1])
        output[2] = 1/abs(output[2])
        if output[0] > math.pi / self.steer_lock: output[0] = math.pi / self.steer_lock
        if output[0] < -math.pi / self.steer_lock: output[0] = -math.pi / self.steer_lock
        self.control.setSteer(output[0] * math.pi)

        gear = self.state.gear
        print("score: "+str(ge[i].fitness))
        print("gear: " + str(gear))
        print("steer: " + str(output[0]))
        print("accel: " + str(output[1]))
        print("break: " + str(output[2]))
        # print("clutch: " + str(output[4]))
        # print("speedX: " + str(self.state.speedX))
        # print("speedY: " + str(self.state.speedY))
        # print("speedZ: " + str(self.state.speedZ))

        if self.state.rpm >6000: gear = gear+1
        elif self.state.rpm < 1500: gear = gear-1
        if gear > 6: gear = 6
        if gear < 1: gear = 1

        self.control.setGear(gear)
        if output[1] < 0: output[1] = 0
        if output[1] > 1: output[1] = 1
        self.control.setAccel(output[1])

        if output[2] < 0: output[2] = 0
        if output[2] > 1: output[2] = 1
        self.control.setBrake(output[2])


        return self.control.toMsg()

    def testdrive(self, msg, best):

        self.state.setFromMsg(msg)

        if float(self.state.wheelSpinVel[0]) >= 0:
            wheel1 = float(1 / (self.state.wheelSpinVel[0] + 1))
        else:
            wheel1 = - float(1/(abs(self.state.wheelSpinVel[0]) + 1))

        if float(self.state.wheelSpinVel[1]) >= 0:
            wheel2 = float(1 / (self.state.wheelSpinVel[1] + 1))
        else:
            wheel2 = - float(1 / (abs(self.state.wheelSpinVel[1]) + 1))

        if float(self.state.wheelSpinVel[2]) >= 0:
            wheel3 = float(1 / (self.state.wheelSpinVel[2] + 1))
        else:
            wheel3 = - float(1 / (abs(self.state.wheelSpinVel[2]) + 1))

        if float(self.state.wheelSpinVel[3]) >= 0:
            wheel4 = float(1 / (self.state.wheelSpinVel[3] + 1))
        else:
            wheel4 = - float(1 / (abs(self.state.wheelSpinVel[3]) + 1))


        data = [
            float(self.state.angle / math.pi),
            float(1/(self.state.damage+1)),
            float(1/(self.state.fuel+1)),
            self.state.gear/6,
            # float(self.state.opponents[0]) / 200,
            # float(self.state.opponents[1]) / 200,
            # float(self.state.opponents[2]) / 200,
            # float(self.state.opponents[3]) / 200,
            # float(self.state.opponents[4]) / 200,
            # float(self.state.opponents[5]) / 200,
            # float(self.state.opponents[6]) / 200,
            # float(self.state.opponents[7]) / 200,
            # float(self.state.opponents[8]) / 200,
            # float(self.state.opponents[9]) / 200,
            # float(self.state.opponents[10]) / 200,
            # float(self.state.opponents[11]) / 200,
            # float(self.state.opponents[12]) / 200,
            # float(self.state.opponents[13]) / 200,
            # float(self.state.opponents[14]) / 200,
            # float(self.state.opponents[15]) / 200,
            # float(self.state.opponents[16]) / 200,
            # float(self.state.opponents[17]) / 200,
            # float(self.state.opponents[18]) / 200,
            # float(self.state.opponents[19]) / 200,
            # float(self.state.opponents[20]) / 200,
            # float(self.state.opponents[21]) / 200,
            # float(self.state.opponents[22]) / 200,
            # float(self.state.opponents[23]) / 200,
            # float(self.state.opponents[24]) / 200,
            # float(self.state.opponents[25]) / 200,
            # float(self.state.opponents[26]) / 200,
            # float(self.state.opponents[27]) / 200,
            # float(self.state.opponents[28]) / 200,
            # float(self.state.opponents[29]) / 200,
            # float(self.state.opponents[30]) / 200,
            # float(self.state.opponents[31]) / 200,
            # float(self.state.opponents[32]) / 200,
            # float(self.state.opponents[33]) / 200,
            # float(self.state.opponents[34]) / 200,
            # float(self.state.opponents[35]) / 200,
            # self.state.opponents,
            # self.state.racePos,
            float(1/(self.state.rpm+1)),
            float(self.state.speedX/1000),
            float(self.state.speedY/1000),
            float(self.state.speedZ/1000),
            float(self.state.track[0]) / 200,
            float(self.state.track[1]) / 200,
            float(self.state.track[2]) / 200,
            float(self.state.track[3]) / 200,
            float(self.state.track[4]) / 200,
            float(self.state.track[5]) / 200,
            float(self.state.track[6]) / 200,
            float(self.state.track[7]) / 200,
            float(self.state.track[8]) / 200,
            float(self.state.track[9]) / 200,
            float(self.state.track[10]) / 200,
            float(self.state.track[11]) / 200,
            float(self.state.track[12]) / 200,
            float(self.state.track[13]) / 200,
            float(self.state.track[14]) / 200,
            float(self.state.track[15]) / 200,
            float(self.state.track[16]) / 200,
            float(self.state.track[17]) / 200,
            float(self.state.track[18]) / 200,
            float(self.state.trackPos/5),
            wheel1,
            wheel2,
            wheel3,
            wheel4,
            float(self.state.z/100),
        ]
        output = best.activate(data)
        # normalize = [abs(output[1]), abs(output[2])]
        # maximum = max(normalize)
        output[1] = 1/abs(output[1])
        output[2] = 1/abs(output[2])
        if output[0] > math.pi / self.steer_lock: output[0] = math.pi / self.steer_lock
        if output[0] < -math.pi / self.steer_lock: output[0] = -math.pi / self.steer_lock
        self.control.setSteer(output[0] * math.pi)

        gear = self.state.gear
        print("gear: " + str(gear))
        print("steer: " + str(output[0]))
        print("accel: " + str(output[1]))
        print("break: " + str(output[2]))
        print("rpm: "+str(self.state.rpm))
        # print("clutch: " + str(output[4]))
        # print("speedX: " + str(self.state.speedX))
        # print("speedY: " + str(self.state.speedY))
        # print("speedZ: " + str(self.state.speedZ))

        if self.state.rpm > 6000:
            gear = gear + 1
        elif self.state.rpm < 1500:
            gear = gear - 1
        if gear > 6: gear = 6
        if gear < 1: gear = 1

        self.control.setGear(gear)
        if output[1] < 0: output[1] = 0
        if output[1] > 1: output[1] = 1
        self.control.setAccel(output[1])

        if output[2] < 0: output[2] = 0
        if output[2] > 1: output[2] = 1
        self.control.setBrake(output[2])

        return self.control.toMsg()

    def onShutDown(self):
        print("best lap: " + str(self.state.lastLapTime))

        pass

    def onRestart(self):
        print("best lap: " + str(self.state.lastLapTime))
        pass
