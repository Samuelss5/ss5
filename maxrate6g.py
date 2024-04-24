import numpy as np
from math import *
import random
import matplotlib.pyplot as plt

Bandwidth = 90 * 10 ** 6  # 90 megahertz

Band = 180 * 10 ** 3  # 180 kilohertz

constant = 10 ** -4  # path loss constant

k0 = 10 ** -17

cover_area_side = 1000

lowest_distance = 10

band_blocks = Bandwidth / Band

"""
codigo editado as 22:23 do dia 18 de abril de 2023 

    CODIGO MAIS ATUAL!!!!!!!!!!!!!


"""


class System:
    def __init__(self, aps_num, ue_num, cpu_num):
        self.__aps = self.create_aps(aps_num)
        self.__users = self.create_users(ue_num)
        self.__cpus = self.create_cpus(cpu_num)

    def create_aps(self, aps_num):

        if isinstance(aps_num, int):

            dict = {}

            for i in range(aps_num):
                ap = AccessPoint(i)
                dict[ap.id] = ap

            return dict

    def create_users(self, ue_num):

        if isinstance(ue_num, int):

            dict = {}

            for i in range(ue_num):
                x = random.randint(0, 1000)
                y = random.randint(0, 1000)
                user = User(x, y, i)
                dict[user.id] = user

            return dict

    def create_cpus(self, cpu_num):

        if isinstance(cpu_num, int):

            dict = {}
            for i in range(cpu_num):
                cpu = Cpu(20, 20, i)
                dict[cpu.id] = cpu

            return dict

    @property
    def users(self):
        return self.__users

    @property
    def aps(self):
        return self.__aps

    @property
    def cpus(self):
        return self.__cpus

    def set_app_position(self):
        number = np.sqrt(len(self.__aps))

        interval = (cover_area_side / number) / 2

        start_point = interval / 2

        coordinates = []
        for i in range(int(number)):
            for j in range(int(number)):
                x = (j * 2 + 1) * interval
                y = (i * 2 + 1) * interval
                coordinates.append([x, y])

        for i in range(len(coordinates)):
            self.__aps[i].x = coordinates[i][0]
            self.__aps[i].y = coordinates[i][1]

    def connection(self):

        """
        connection: VOID
        return: this function walks the self.__aps attribute and calculate the power received
        from the user at each ap, selecting the 3 aps that receive highest power and the user
        keeps to itself a reference of the aps which he is connected to.
        """

        for i in self.__users:
            user = self.__users[i]

            pr_by_aps = {}  # the power received from the user K at each L ap

            for j in self.__aps:
                ap = self.__aps[j]

                distance = np.sqrt((ap.x - user.x) ** 2 + (ap.y - user.y) ** 2)

                if distance < lowest_distance:
                    user.y = 10

                new_distance = np.sqrt((ap.x - user.x) ** 2 + (ap.y - user.y) ** 2)

                shadowing = exp(np.random.normal(0, 2, 1)[0])
                # shadowing log normal random variable

                received_power = shadowing * user.tpower * (constant / (new_distance ** 4))

                pr_by_aps[j] = received_power

            higher1 = 0  # auxiliary variable to store the highest power received

            ap1 = None  # auxiliary variable to store the id of the ap that receives the
            # highest received power

            higher2 = 0  # auxiliary variable to store the Second highest power received

            ap2 = None  # auxiliary variable to store the id of the ap that receives the
            # second highest received power

            higher3 = 0  # auxiliary variable to store the Third highest power received

            ap3 = None  # auxiliary variable to store the id of the ap that receives the
            # third highest received power

            for j in pr_by_aps:
                if pr_by_aps[j] > higher1:
                    higher1 = pr_by_aps[j]
                    ap1 = j

            pr_by_aps.pop(ap1)

            for j in pr_by_aps:
                if pr_by_aps[j] > higher2:
                    higher2 = pr_by_aps[j]
                    ap2 = j

            pr_by_aps.pop(ap2)

            for j in pr_by_aps:
                if pr_by_aps[j] > higher3:
                    higher3 = pr_by_aps[j]
                    ap3 = j

            user.aps = [ap1, ap2, ap3]
            self.__aps[ap1].links = [user, higher1]
            self.__aps[ap2].links = [user, higher2]
            self.__aps[ap3].links = [user, higher3]

    def distribution(self):
        for i in self.__aps:
            ap = self.__aps[i]

            cpus_distances = {}
            lowest_distance = 0
            cpu_id = 0

            for j in self.__cpus:
                cpu = self.__cpus[j]

                distance = np.sqrt((cpu.x - ap.x) ** 2 + (cpu.y - ap.y) ** 2)

                cpus_distances[cpu.id] = distance

                if distance < lowest_distance:
                    lowest_distance = distance
                    cpu_id = cpu.id

            self.__cpus[cpu_id].aps = ap

    def schedule(self):
        higher_throughput = 0

        for i in self.__aps:
            ap = self.__aps[i]

            ue_num = len(ap.links)
            if ue_num == 0:
                pass

            else:
                links_power = {}
                for j in ap.links:
                    channel_power = ap.links[j].power

                    noise_power_block = Bandwidth * k0

                    snr = channel_power / noise_power_block

                    links_power[j] = snr


                sorted_snr = dict(sorted(links_power.items(), key=lambda item: item[1]))


                all_users_in_ap = []

                for i in sorted_snr:
                    all_users_in_ap.append(i)

                num = int(len(all_users_in_ap) * 0.8)

                users_schedule = all_users_in_ap[num:]

                each_user_band = ( band_blocks // len(users_schedule) ) * Band

                for j in users_schedule:
                    ap.links[j].band = each_user_band




















    def capacity_experience(self):
        ues_rates = []

        for i in self.__users:
            user = self.__users[i]

            aps = user.aps

            ap1 = self.__aps[aps[0]]
            ap2 = self.__aps[aps[1]]
            ap3 = self.__aps[aps[2]]




            total_power = ap1.links[user.id].power + ap2.links[user.id].power + ap3.links[user.id].power

            total_band = ap1.links[user.id].band + ap2.links[user.id].band + ap3.links[user.id].band

            if total_band != 0:

                noise_power = k0 * total_band



                snr = total_power / noise_power

                capacity = total_band * log2(1 + snr)

                ues_rates.append(capacity / 10 ** 9)

            else:

                pass

        return ues_rates

    def snr_experience(self):
        users_snr = []
        for i in self.__users:
            user = self.__users[i]

            aps = user.aps

            ap1 = self.__aps[aps[0]]
            ap2 = self.__aps[aps[1]]
            ap3 = self.__aps[aps[2]]

            total_power = ap1.links[user.id].power + ap2.links[user.id].power + ap3.links[user.id].power

            total_band = ap1.links[user.id].band + ap2.links[user.id].band + ap3.links[user.id].band

            if total_band != 0:
                noise_power = k0 * total_band

                snr = total_power / noise_power

                users_snr.append(snr)

            else:
                pass

        return users_snr

    # def throughput(self):

    # for i in self.__users:
    #  user = self.__users[i]

    # aps = user.aps

    #  ap1 = self.__aps[aps[0]]
    # ap2 = self.__aps[aps[1]]
    #  ap3 = self.__aps[aps[2]]

    #  total_power = ap1.links[user.id].power + ap2.links[user.id].power + ap3.links[user.id].power

    #  total_band = ap1.links[user.id].band + ap2.links[user.id].band + ap3.links[user.id].band

    #  noise_power = k0 * total_band

    #  snr = total_band / noise_power

    #  capacity = total_band * log2(1 + snr)

    # spectral_efficiency = capacity / total_band


class Cpu:
    def __init__(self, x, y, id):
        self.__id = id
        self.__x = x
        self.__y = y
        self.__aps = {}

    @property
    def id(self):
        return self.__id

    @property
    def x(self):
        return self.__x

    @property
    def y(self):
        return self.__y

    @property
    def aps(self):
        return self.__aps

    @aps.setter
    def aps(self, ap):
        if isinstance(ap, AccessPoint):
            self.__aps[ap.id] = ap


class AccessPoint:
    def __init__(self, id):
        self.__id = id
        self.__links = {}
        self.__x = 0
        self.__y = 0
        self.__blocks = []

    @property
    def x(self):
        return self.__x

    @property
    def y(self):
        return self.__y

    @x.setter
    def x(self, value):
        if isinstance(value, float):
            self.__x = value

    @y.setter
    def y(self, value):
        if isinstance(value, float):
            self.__y = value

    @property
    def id(self):
        return self.__id

    @property
    def links(self):
        return self.__links

    @links.setter
    def links(self, value):
        if isinstance(value, list):
            self.__links[value[0].id] = Channel(value[0], value[1])

    @property
    def blocks(self):
        return self.__blocks

    def schedule(self):

        if self.__blocks.size % len(self.__links) != 0:
            each_user_band = self.__blocks.size // len(self.__links)
            for i in self.__links:
                channel = self.__links[i]
                channel.band = each_user_band


class Channel:
    def __init__(self, user, power):
        self.__user = user
        self.__power = power
        self.__id = user.id
        self.__band = 0

    @property
    def id(self):
        return self.__id

    @property
    def user(self):
        return self.__user

    @property
    def power(self):
        return self.__power

    @property
    def band(self):
        return self.__band

    @band.setter
    def band(self, value):
        self.__band = value

    @property
    def capacity(self):
        noise_power = Band * k0
        snr = self.__power / noise_power
        capacity = Band * log2(1 + snr)

        return capacity / 10 ** 6




    @property
    def necessary_blocks(self):
        blocks = self.__user.amount_data // self.capacity + 1
        return blocks


class User:
    def __init__(self, x, y, id):
        self.__id = id
        self.__x = x
        self.__y = y
        self.__aps = None
        self.__tpower = 1000  # milliwatts
        self.__amount_data =  10 * 10 ** 9  # 1Megabit

    @property
    def x(self):
        return self.__x

    @x.setter
    def x(self, value):
        self.__x += value

    @property
    def y(self):
        return self.__y

    @y.setter
    def y(self, value):
        self.__y += value

    @property
    def id(self):
        return self.__id

    @property
    def aps(self):
        return self.__aps

    @aps.setter
    def aps(self, value):
        if isinstance(value, list):
            self.__aps = value

    @property
    def tpower(self):
        return self.__tpower

    @property
    def amount_data(self):
        return self.__amount_data


def main():
    users_10_capacity = []
    users_10_snr = []

    for i in range(1000):
        system = System(36, 10, 1)
        system.set_app_position()

        system.connection()

        system.schedule()

        users_10_capacity.extend(system.capacity_experience())
        users_10_snr.extend(system.snr_experience())



    users_20_capacity = []
    users_20_snr = []

    for i in range(1000):
        system = System(36, 20, 1)
        system.set_app_position()
        system.connection()
        system.schedule()
        users_20_capacity.extend(system.capacity_experience())
        users_20_snr.extend(system.snr_experience())

    users_30_capacity = []
    users_30_snr = []

    for i in range(1000):
        system = System(36, 30, 1)
        system.set_app_position()
        system.connection()
        system.schedule()
        users_30_capacity.extend(system.capacity_experience())
        users_30_snr.extend(system.snr_experience())


    # capacity plot
    plt.xlabel('Channel capacity in Gbps')
    plt.ylabel('CDF')
    plt.plot(np.sort(users_10_capacity), np.arange(0,len(users_10_capacity)) / len(users_10_capacity), label = '10 users')
    plt.plot(np.sort(users_20_capacity), np.arange(0,len(users_20_capacity)) / len(users_20_capacity), label = '20 users')
    plt.plot(np.sort(users_30_capacity), np.arange(0,len(users_30_capacity)) / len(users_30_capacity), label = '30 users')
    plt.grid()

    # snr plot

    #plt.xlabel('SNR in dB')
   # plt.ylabel('CDF')
    snr_10_dB = [10*log10(users_10_snr[i]) for i in range(len(users_10_snr))]
    snr_20_dB = [10*log10(users_20_snr[i]) for i in range(len(users_20_snr))]
    snr_30_dB = [10*log10(users_30_snr[i]) for i in range(len(users_30_snr))]


    #plt.plot(np.sort(snr_10_dB), np.arange(0,len(snr_10_dB)) / len(snr_10_dB), label = '10 users')
    #plt.plot(np.sort(snr_20_dB), np.arange(0, len(snr_20_dB)) / len(snr_20_dB), label = '20 users')
    #plt.plot(np.sort(snr_30_dB), np.arange(0, len(snr_30_dB)) / len(snr_30_dB), label = '30 users')
    plt.show()











main()
