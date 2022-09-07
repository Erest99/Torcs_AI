import math

import msgParser
import carState
import carControl

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
        if self.state.damage > 1000:
            ge[i].fitness = -100000
            self.control.setMeta(1)

        data = [
            int(self.state.angle * 100),
            int(self.state.damage),
            int(self.state.fuel * 10),
            self.state.gear,
            int(self.state.opponents[0]) / 200,
            int(self.state.opponents[1]) / 200,
            int(self.state.opponents[2]) / 200,
            int(self.state.opponents[3]) / 200,
            int(self.state.opponents[4]) / 200,
            int(self.state.opponents[5]) / 200,
            int(self.state.opponents[6]) / 200,
            int(self.state.opponents[7]) / 200,
            int(self.state.opponents[8]) / 200,
            int(self.state.opponents[9]) / 200,
            int(self.state.opponents[10]) / 200,
            int(self.state.opponents[11]) / 200,
            int(self.state.opponents[12]) / 200,
            int(self.state.opponents[13]) / 200,
            int(self.state.opponents[14]) / 200,
            int(self.state.opponents[15]) / 200,
            int(self.state.opponents[16]) / 200,
            int(self.state.opponents[17]) / 200,
            int(self.state.opponents[18]) / 200,
            int(self.state.opponents[19]) / 200,
            int(self.state.opponents[20]) / 200,
            int(self.state.opponents[21]) / 200,
            int(self.state.opponents[22]) / 200,
            int(self.state.opponents[23]) / 200,
            int(self.state.opponents[24]) / 200,
            int(self.state.opponents[25]) / 200,
            int(self.state.opponents[26]) / 200,
            int(self.state.opponents[27]) / 200,
            int(self.state.opponents[28]) / 200,
            int(self.state.opponents[29]) / 200,
            int(self.state.opponents[30]) / 200,
            int(self.state.opponents[31]) / 200,
            int(self.state.opponents[32]) / 200,
            int(self.state.opponents[33]) / 200,
            int(self.state.opponents[34]) / 200,
            int(self.state.opponents[35]) / 200,
            # self.state.opponents,
            # self.state.racePos,
            int(self.state.rpm),
            int(self.state.speedX),
            int(self.state.speedY),
            int(self.state.speedZ),
            int(self.state.track[0]) / 200,
            int(self.state.track[1]) / 200,
            int(self.state.track[2]) / 200,
            int(self.state.track[3]) / 200,
            int(self.state.track[4]) / 200,
            int(self.state.track[5]) / 200,
            int(self.state.track[6]) / 200,
            int(self.state.track[7]) / 200,
            int(self.state.track[8]) / 200,
            int(self.state.track[9]) / 200,
            int(self.state.track[10]) / 200,
            int(self.state.track[11]) / 200,
            int(self.state.track[12]) / 200,
            int(self.state.track[13]) / 200,
            int(self.state.track[14]) / 200,
            int(self.state.track[15]) / 200,
            int(self.state.track[16]) / 200,
            int(self.state.track[17]) / 200,
            int(self.state.track[18]) / 200,
            int(self.state.trackPos),
            int(self.state.wheelSpinVel[0]),
            int(self.state.wheelSpinVel[1]),
            int(self.state.wheelSpinVel[2]),
            int(self.state.wheelSpinVel[3]),
            int(self.state.z),
        ]
        output = nets[i].activate(data)
        if output[0] > math.pi / self.steer_lock: output[0] = math.pi / self.steer_lock
        if output[0] < -math.pi / self.steer_lock: output[0] = -math.pi / self.steer_lock

        gear = round(output[1] * 6)
        self.control.setSteer(output[0] * math.pi)
        print("gear: " + str(output[1]))
        print("steer: " + str(output[0]))
        print("accel: " + str(output[2]))
        print("break: " + str(output[3]))
        print("clutch: " + str(output[4]))
        # print("speedX: " + str(self.state.speedX))
        # print("speedY: " + str(self.state.speedY))
        # print("speedZ: " + str(self.state.speedZ))

        if gear > 6: gear = 6
        if gear < -1: gear = -1

        self.control.setGear(gear)
        if output[2] < 0: output[2] = 0
        if output[2] > 1: output[2] = 1
        self.control.setAccel(output[2])

        if output[2] < 0: output[3] = 0
        if output[2] > 1: output[3] = 1
        self.control.setBrake(output[3])

        if output[2] < 0: output[4] = 0
        if output[2] > 1: output[4] = 1
        self.control.setClutch(output[4])

        return self.control.toMsg()

    def testdrive(self, msg, best):

        self.state.setFromMsg(msg)
        data = [
            int(self.state.angle * 100),
            int(self.state.damage),
            int(self.state.fuel * 10),
            self.state.gear,
            int(self.state.opponents[0]) / 200,
            int(self.state.opponents[1]) / 200,
            int(self.state.opponents[2]) / 200,
            int(self.state.opponents[3]) / 200,
            int(self.state.opponents[4]) / 200,
            int(self.state.opponents[5]) / 200,
            int(self.state.opponents[6]) / 200,
            int(self.state.opponents[7]) / 200,
            int(self.state.opponents[8]) / 200,
            int(self.state.opponents[9]) / 200,
            int(self.state.opponents[10]) / 200,
            int(self.state.opponents[11]) / 200,
            int(self.state.opponents[12]) / 200,
            int(self.state.opponents[13]) / 200,
            int(self.state.opponents[14]) / 200,
            int(self.state.opponents[15]) / 200,
            int(self.state.opponents[16]) / 200,
            int(self.state.opponents[17]) / 200,
            int(self.state.opponents[18]) / 200,
            int(self.state.opponents[19]) / 200,
            int(self.state.opponents[20]) / 200,
            int(self.state.opponents[21]) / 200,
            int(self.state.opponents[22]) / 200,
            int(self.state.opponents[23]) / 200,
            int(self.state.opponents[24]) / 200,
            int(self.state.opponents[25]) / 200,
            int(self.state.opponents[26]) / 200,
            int(self.state.opponents[27]) / 200,
            int(self.state.opponents[28]) / 200,
            int(self.state.opponents[29]) / 200,
            int(self.state.opponents[30]) / 200,
            int(self.state.opponents[31]) / 200,
            int(self.state.opponents[32]) / 200,
            int(self.state.opponents[33]) / 200,
            int(self.state.opponents[34]) / 200,
            int(self.state.opponents[35]) / 200,
            # self.state.opponents,
            # self.state.racePos,
            int(self.state.rpm),
            int(self.state.speedX),
            int(self.state.speedY),
            int(self.state.speedZ),
            int(self.state.track[0]) / 200,
            int(self.state.track[1]) / 200,
            int(self.state.track[2]) / 200,
            int(self.state.track[3]) / 200,
            int(self.state.track[4]) / 200,
            int(self.state.track[5]) / 200,
            int(self.state.track[6]) / 200,
            int(self.state.track[7]) / 200,
            int(self.state.track[8]) / 200,
            int(self.state.track[9]) / 200,
            int(self.state.track[10]) / 200,
            int(self.state.track[11]) / 200,
            int(self.state.track[12]) / 200,
            int(self.state.track[13]) / 200,
            int(self.state.track[14]) / 200,
            int(self.state.track[15]) / 200,
            int(self.state.track[16]) / 200,
            int(self.state.track[17]) / 200,
            int(self.state.track[18]) / 200,
            int(self.state.trackPos),
            int(self.state.wheelSpinVel[0]),
            int(self.state.wheelSpinVel[1]),
            int(self.state.wheelSpinVel[2]),
            int(self.state.wheelSpinVel[3]),
            int(self.state.z),
        ]
        output = best.activate(data)
        if output[0] > math.pi / self.steer_lock: output[0] = math.pi / self.steer_lock
        if output[0] < -math.pi / self.steer_lock: output[0] = -math.pi / self.steer_lock
        self.control.setSteer(output[0] * math.pi)

        gear = round(output[1] * 6)
        if gear > 6: gear = 6
        if gear < -1: gear = -1

        self.control.setGear(gear)
        if output[2] < 0: output[2] = 0
        if output[2] > 1: output[2] = 1
        self.control.setAccel(output[2])

        if output[2] < 0: output[3] = 0
        if output[2] > 1: output[3] = 1
        self.control.setBrake(output[3])

        if output[2] < 0: output[4] = 0
        if output[2] > 1: output[4] = 1
        self.control.setClutch(output[4])

        return self.control.toMsg()

    def onShutDown(self):
        print("best lap: " + str(self.state.lastLapTime))

        pass

    def onRestart(self):
        print("best lap: " + str(self.state.lastLapTime))
        pass
