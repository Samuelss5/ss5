import random
from math import*
import copy
import matplotlib.pyplot as plt
import numpy as np
#constants for the propagation model
c = 10**-4
n = 4
d0 = 1 #meter
UEtp = 1 #user transmit power

#raio da area de cobertura
cover_r = 1000 #metros


#def noisepower(bandwith)

def noisepower(bandwith, constant, channels_n):
    return constant*(bandwith/channels_n)

def receivedpower(distance, constant, tpower):
    if distance == 0:
        rpower = 1
    else:
        rpower = tpower*(constant/(distance**n))

    return rpower

#minimun received power
minpow = UEtp*(c/ (cover_r)**n)

#constant for the noise power
K0 =10**-17

#total Bandwith
BANDWITH = 100*(10**6)#megahertz


class User():
    def __init__(self):
        self._coordX = random.randint(-3000,3000)
        self._coordY = random.randint(-3000,3000)
        self._tpower = UEtp
        self._chip = random.randint(0,1000)

    @property
    def coordx(self):
        return self._coordX

    @property
    def coordy(self):
        return self._coordY

    def move(self):
        dist = random.randint(0,10)
        self._coordX += dist
        self._coordY += dist

    @property
    def tpower(self):
        return self._tpower

    @property
    def chip(self):
        return self._chip

    def connection(self, system_):
        if isinstance(system_, System):
            system_.alocation(self)
class Erb:
    numb = 0
    def __init__(self, x_, y_):
        self._channels = {1 :[], 2 :[], 3 :[], 4 :[], 5 :[]}
        self._Qos = {1 :[], 2 :[], 3 :[], 4 :[], 5 :[]}
        self._sirs = {1 :[], 2 :[], 3 :[], 4 :[], 5 :[]}
        self._connectedusers = []
        self._coordX = x_
        self._coordY = y_
        self._erbnumb = Erb.numb   # identification number of the erb
        Erb.numb += 1    #setter for the identification number of the ap

    @property
    def coordx(self):
        return self._coordX


    @property
    def coordy(self):
        return self._coordY

    @coordx.setter
    def coordx(self, value):
        if isinstance(value, int):
            self._coordX += value

    @coordy.setter
    def coordy(self, value):
        if isinstance(value, int):
            self._coordY += value

    @property
    def erbnumb(self):
        return self._erbnumb

    @property
    def channels(self):
        return self._channels





class System():
    def __init__(self):
        self._Usersnumbers = []
        self._erbs = {}
        self._snrs = {1:0, 2:0, 3:0}


    def receivedpower(self, user, ap):
        if isinstance(user, User) and isinstance(ap, Erb):
            distance = sqrt(   (ap.coordx - user.coordx)**2 + (ap.coordy - user.tpower)**2   )
            rpower = user.tpower*(c/  (distance)**n)
            return rpower

    def distance(self, user, ap):
        distance = sqrt((ap.coordx - user.coordx) ** 2 + (ap.coordy - user.tpower) ** 2)
        return distance

    def alocation(self, user):
        maior = 0   #auxiliary variable that assumes the value of the biggest power received by the ap
        erb_n = 0   #auxiliary variable that assumes the number of the erb that is nearest to the user
        for i in self._erbs:
           distance = sqrt((self._erbs[i].coordx - user.coordx) ** 2 + (self._erbs[i].coordy - user.coordy) ** 2)
           r_power = receivedpower(distance, c, user.tpower)
           if r_power > maior:
                maior = r_power
                erb_n = i
           else:
                pass

        void_c = 0
        fisrt = list(self._erbs[erb_n].channels.keys())[0]  #primeira chave do dicionario de canais
        x = len(self._erbs[erb_n].channels[fisrt])
        for i in self._erbs[erb_n].channels:
            if len(self._erbs[erb_n].channels[i]) <= x:
                x = len(self._erbs[erb_n].channels[i])
                void_c = i


        if maior > minpow:
                self._erbs[erb_n].channels[void_c].append(user)



    def add_erb(self, erb):
        if isinstance(erb, Erb):
            coords = []
            for i in self._erbs:
                coords.append([self._erbs[i].coordx, self._erbs[i].coordy])
            while True:
                if [erb.coordx, erb.coordy] in coords:
                    erb.coordx = 800
                else:
                    break
            self._erbs[erb.erbnumb] = erb

    @property
    def erbs(self):
        return self._erbs


    @property
    def noise_power(self):
        return self._snrs

    @noise_power.setter
    def noise_power(self):
        for i in self._erbs:
            n = len(self._erbs[i].channels)
            self._snrs[i] = noisepower(BANDWITH, K0,n)

    def snr(self):
        snrvector = []
        for i in self._erbs:
            for j in self._erbs[i].channels:
                for z in self._erbs[i].channels[j]:
                    rp = self.receivedpower(z, self._erbs[i])
                    noise = noisepower(BANDWITH, K0, len(self._erbs[i].channels))
                    snrvector.append(rp / noise)

        return snrvector

    def sinr(self):
        sinrvector = []
        for i in self._erbs:
            for j in self._erbs[i].channels:
                userspowers = []
                usersnoise = []
                for z in self._erbs[i].channels[j]:
                    noise = noisepower(BANDWITH, K0, len(self._erbs[i].channels))
                    rp = self.receivedpower(z, self._erbs[i])
                    userspowers.append(rp)
                    usersnoise.append(noise)

                for w in range(len(userspowers)):
                    sinr = userspowers[w]/((sum(userspowers) - userspowers[w]) + usersnoise[w])
                    sinrvector.append(sinr)

        return sinrvector

    def qos(self):
        qoslist = []
        for i in self._erbs:
            for j in self._erbs[i].channels:
                userspowers = []
                usersnoise = []
                band = []
                for z in self._erbs[i].channels[j]:
                    noise = noisepower(BANDWITH, K0, len(self._erbs[i].channels))
                    rp = self.receivedpower(z, self._erbs[i])
                    userspowers.append(rp)
                    usersnoise.append(noise)
                    band.append(BANDWITH/len(self._erbs[i].channels))

                for w in range(len(userspowers)):
                    sinr = userspowers[w] / ((sum(userspowers) - userspowers[w]) + usersnoise[w])
                    qos = (band[w])*(1 + sinr)
                    qoslist.append(qos)

        return qoslist

def main():
    qoslist = []
    sinrlist = []
    erbsnum = 3
    erbsx = []
    erbsy = []
    for i in range(10):


        system = System()
        for j in range(erbsnum):
            erb = Erb(0,0)
            system.add_erb(erb)
            erbsx.append(erb.coordx)
            erbsy.append(erb.coordy)



        for i in range(10):
            user = User()
            user.connection(system)
        sinrlist.extend(system.sinr())
        qoslist.extend(system.qos())

    print(len(sinrlist))




    sinr_db = [10*log10(sinrlist[i]) for i in range(len(sinrlist))]
    print(len(sinr_db))
    plt.subplot(1,2,1)
    x = np.sort(sinr_db)
    print(x)
    y = np.arange(0, len(sinr_db)) / len(sinr_db)
    plt.xlabel('sinr[dB]')
    plt.ylabel('CDF')
    plt.plot(x,y)
    qostarget = [10*log(qoslist[i]) for i in range(len(qoslist))]
    print(qostarget)
    print(np.sort(qostarget))
    plt.subplot(1,2,2)
    xs = np.sort(qostarget)
    ys = np.arange(0, len(qostarget)) / len(qostarget)
    plt.xlabel('QOS[Mbps]')
    plt.ylabel('CDF')
    plt.plot(xs,ys)
    plt.show()


if __name__ == "__main__":
    main()