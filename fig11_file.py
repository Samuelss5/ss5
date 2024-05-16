
import random
import numpy as np

def lin2db(x):
    return 10*np.log10(x)

def db2lin(x):
    return 10**(x/10)
L = 400 # coverage area side

bandwidth = 10 * 10**6

class User:
    def __init__(self, id, x, y):
        self.__id = id
        self.__x = x
        self.__y = y

    @property
    def id(self):
        return self.__id

    @property
    def x(self):
        return self.__x

    @property
    def y(self):
        return self.__y


class AccessPoint:
    def __init__(self, id):
        self.__id = id
        self.__x = 0
        self.__y = 0

    @property
    def id(self):
        return self.__id


    @property
    def x(self):
        return self.__x

    @x.setter
    def x(self, x):
        self.__x += x

    @property
    def y(self):
        return self.__y

    @y.setter
    def y(self, y):
        self.__y += y


class System:
    def __init__(self):
        self.__users = None
        self.__aps = None
        self.__cpus = None
        self.__channels = None


    @property
    def users(self):
        return self.__users

    @property
    def aps(self):
        return self.__aps

    def creatUsers(self, ue_num):
        if isinstance(ue_num, int):
            users = {}

            for i in range(ue_num):
                x = random.randint(0,L)
                y = random.randint(0,L)
                user = User(i, x, y)
                users[user.id] = user

            self.__users = users


    def creatAPs(self, ap_num):
        if isinstance(ap_num, int):
            aps = {}

            for i in range(ap_num):
                ap = AccessPoint(i)
                aps[ap.id] = ap

            self.__aps = aps


    def creatCpus(self, cpu_num):

        if isinstance(cpu_num, int):

            cpus = {}
            for i in range(cpu_num):
                cpu = AccessPoint(i)
                cpus[cpu.id] = cpu

            self.__cpus = cpus

    def set_ap_position(self):
        number = np.sqrt(len(self.__aps))

        interval = (L / number) / 2

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

    def channel_matrix(self):

        k = len(self.__users)

        m = len(self.__aps)

        channel_matrix = np.zeros((k, m))

        for i in range(k):

            ue = self.__users[i]


            for j in range(m):

                ap = self.__aps[j]

                horiz_distance = np.sqrt((ue.x - ap.x) ** 2 + (ue.y - ap.y)**2)


                #print(horiz_distance)

                snr = db2lin( 2 * np.random.randn() + 10 + 96 - 30.5 - 36.7 * np.log10(np.sqrt(horiz_distance**2 + 100))) # 100 = antenna height ** 2

                #snr_vector[j] = snr

                channel = np.sqrt(snr)





                channel_matrix[i][j] = channel







        self.__channels = channel_matrix


    def mmse_sinr(self):

        k = len(self.__users)
        m = len(self.__aps)

        h = self.__channels

        sinr_cell_free = []

        for i in range(k):

            sum = 0
            for j in range(k):

                if j != i:
                    sum += h[j] @ h[j].T


            plus = sum + np.eye(m)


            sinr = h[i].T @ (np.linalg.inv(plus)) @ h[i]

            sinr_cell_free.append(lin2db(sinr))



        auxi_list = sinr_cell_free.copy()
        c = 0
        best_users = []
        while c < m:
            higher = 0
            ue = 0

            for i in range(k):
                if auxi_list[i] > higher:
                    higher = auxi_list[i]
                    ue = i

                else:
                    pass

            best_users.append(ue)
            auxi_list[ue] = 0

            c += 1

        new_list = np.sort(best_users)
        new_matrix = np.zeros((len(best_users), m))



        for i in range(len(best_users)):
            x = new_list[i]
            new_matrix[i] = h[x]



        sinr_scheduled_users = []

        for i in range(m):
            schedule_sum = 0

            for j in range(m):

                if j != i:
                    schedule_sum += new_matrix[j] @ new_matrix[j].T

            plus_schedule = schedule_sum + np.eye(m)



            sinr = new_matrix[i].T @ (np.linalg.inv(plus_schedule)) @ new_matrix[i]

            capacity = bandwidth * np.log2(1 + sinr)

            #sinr_scheduled_users.append(lin2db(sinr))

            sinr_scheduled_users.append(capacity/10**6)

        number = k - m

        for i in range(number):
            sinr_scheduled_users.append(0)

        return sinr_scheduled_users




    def robin_schedule(self):

        k = len(self.__users)

        m = len(self.__aps)

        h = self.__channels

        random_users = []

        c = 0
        while c < m:

            x = random.randint(0,m - 1)

            if x not in random_users:
                random_users.append(x)
                c += 1
            else:
                pass



        new_list = np.sort(random_users)

        new_matrix = np.zeros((m,m))

        for i in range(m):
            x = new_list[i]
            new_matrix[i] = h[x]


        sinr_scheduled_users = []

        for i in range(m):
            schedule_sum = 0

            for j in range(m):
                if j != 0:
                    schedule_sum += new_matrix[j] @ new_matrix[j].T

            plus_schedule = schedule_sum + np.eye(m)

            sinr = new_matrix[i] @ np.linalg.inv(plus_schedule) @ new_matrix[i]

            capacity = bandwidth * np.log2(1 + sinr)
            sinr_scheduled_users.append(capacity/10**6)
            #sinr_scheduled_users.append(lin2db(sinr))

        number = k - m

        for i in range(number):
            sinr_scheduled_users.append(0)

        return sinr_scheduled_users
































            # sinr_k = (h[i].T * np.linalg.inv(h @ h.T - h[i] @ h[i].T + np.eye(m))) @ h[i]

            #print(sinr_k)


            #sinr_cell_free.append(lin2db(sinr_k))

        #return sinr_cell_free








           # sinr = desiredChannel.T * ((h * h.T - ))

        #print(  desiredChannel.T @((h @ h.T - desiredChannel @ desiredChannel.T + np.eye(m) )/desiredChannel) .shape)





            #sinr_k = desiredChannel * desiredChannel.T

            #sinr_k = h * h.T #ok

            #sinr_k = desiredChannel.T @ (( h @ h.T - desiredChannel@desiredChannel.T + np.eye(m)))

            #print(sinr_k.shape)
            #print(desiredChannel)




def main():
    system = System()
    system.creatAPs(36)
    system.set_ap_position()
    system.creatCpus(1)


    lista = []
    lista2 = []

    for i in range(1000):
        system.creatUsers(72)
        system.channel_matrix()

        lista.extend(system.mmse_sinr())
        lista2.extend(system.robin_schedule())



    #system.mmse_sinr()

    #print(np.sort(lista))



    plt.plot(np.sort(lista), np.arange(0,len(lista))/len(lista), label='max rate')
    plt.plot(np.sort(lista2), np.arange(0,len(lista2))/len(lista2), label = 'round robin')
    plt.ylabel('CDF')
    plt.xlabel('capacity in Mbps')
    plt.ylim(0.5,1)
    plt.legend(loc='upper left')
    plt.grid()
    plt.show()


if __name__ == '__main__':

    main()





