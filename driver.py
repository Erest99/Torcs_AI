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

        # fitness = distance from start - current lap time * koeficient - damage * koeficient
        print("distance from start: " + str(self.state.distFromStart) + "\n")
        print("current lap time: " + str(self.state.curLapTime) + "\n")
        # TODO jedna funkce pro NN

        ge[i].fitness = self.state.distFromStart - self.state.curLapTime * 2
        data = [
            self.state.angle,
            self.state.damage,
            self.state.fuel,
            self.state.gear,
            self.state.opponents,
            self.state.racePos,
            self.state.rpm,
            self.state.speedX,
            self.state.speedY,
            self.state.speedZ,
            self.state.track,
            self.state.trackPos,
            self.state.wheelSpinVel,
            self.state.z,
        ]
        output = nets[i].activate(data)
        if output[0] > math.pi/self.steer_lock: output[0] = math.pi/self.steer_lock
        if output[0] < -math.pi/self.steer_lock: output[0] = -math.pi/self.steer_lock
        self.control.setSteer(output[0])
        if output[1] > 5: output[1] = 5
        if output[1] < 1: output[1] = 1
        self.control.setGear(round(output[1]))
        if output[2] < 0: output[2] = 0
        if output[2] > 1: output[2] = 1
        self.control.setAccel(output[2])

        # self.steer(genomes)
        #
        # self.gear(genomes)
        #
        # self.speed(genomes)

        return self.control.toMsg()

    def steer(self, genomes):
        angle = self.state.angle
        dist = self.state.trackPos

        self.control.setSteer((angle - dist * 0.5) / self.steer_lock)

    def gear(self, genomes):
        rpm = self.state.getRpm()
        gear = self.state.getGear()
        angle = self.state.angle
        started = False

        if self.prev_rpm is None:
            up = True
        else:
            if gear < 1:
                started = True
            if (self.prev_rpm - rpm) < 0:
                up = True
            else:
                up = False

        if up and rpm > 7000:
            gear += 1

        if not up and rpm < 3000 and -1 < angle < 1 and started:
            gear -= 1

        self.control.setGear(gear)

    def speed(self, genomes):
        speed = self.state.getSpeedX()
        accel = self.control.getAccel()

        if speed < self.max_speed:
            accel += 0.1
            if accel > 1:
                accel = 1.0
        else:
            accel -= 0.1
            if accel < 0:
                accel = 0.0

        self.control.setAccel(accel)

    def onShutDown(self):
        pass

    def onRestart(self):
        pass
