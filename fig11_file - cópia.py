import itertools
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

            sinr = new_matrix[i] @ np.linalg.inv(plus_schedule) @ new_matrix[i].T


            capacity = bandwidth * np.log2(1 + sinr)
            sinr_scheduled_users.append(capacity/10**6)
            #sinr_scheduled_users.append(lin2db(sinr))

        number = k - m




        return sinr_scheduled_users



    def cesg_schedule(self):

        k = len(self.__users)
        nc = len(self.__aps)
        ues = []
        for i in range(k):
            ues.append(i)

        set_1 = []

        sets_number = k - nc

        argmax_u1 = 0
        u1 = 0

        for i in range(k):

            argmax = self.__channels[i] @ self.__channels[i].T

            if argmax > argmax_u1:
                argmax_u1 = argmax
                u1 = i

            else:
                pass


        set_1.append(u1)
        rate_comparison = 0
        new_user = 0

        l = 1




        while l < nc:

            for i in range(k):
                if i not in set_1:

                    l += 1

                    set_1.append(i)
                    size_set = len(set_1)

                    auxiliar_matrix = np.zeros((size_set,nc))

                    for j in set_1:
                        auxiliar_matrix[set_1.index(j)] = self.__channels[i]

                    sum_rate = 0
                    for j in range(size_set):

                        soma = 0

                        for z in range(size_set):
                            if z != j:
                                soma += auxiliar_matrix[z] @ auxiliar_matrix[z].T

                        plus = soma + np.eye(nc)

                        sinr = auxiliar_matrix[j] @ np.linalg.inv(plus) @ auxiliar_matrix[j].T

                        capacity = bandwidth * np.log2(1 + sinr)
#
                        sum_rate += capacity/10e6

                    if sum_rate > rate_comparison:
                        rate_comparison = sum_rate


                    else:
                        set_1.remove(i)
                        l = l -1


                else:
                    pass


        lista_re = 0
        for i in range(size):
            set_1_vector[0][i] = lista_re[i]


        remanescentes = []
        for i in range(k):
            if i not in lista_re:
                remanescentes.append(i)

        sets_matrix = np.zeros((sets_number, size))

        sets_matrix[0] = set_1_vector

        auxiliar_sets = set_1.copy()

        for i in range(1,sets_number,1):

            best_ue_re = 0
            best_h_re = 0
            for j in remanescentes:
                h = self.__channels[j] @ self.__channels[j].T

                if h > best_h_re:
                    best_h_re = h
                    best_ue_re = j



            lowest_ue_r = 0
            lowest_h_r = self.__channels[u1] @ self.__channels[u1].T

            for j in auxiliar_sets:

                h = self.__channels[j] @ self.__channels[j].T
                if h < lowest_h_r:
                    lowest_h_r = h
                    lowest_ue_r = j

            auxiliar_sets.remove(lowest_ue_r)
            auxiliar_sets.append(best_ue_re)
            if best_ue_re in remanescentes:
                remanescentes.remove(best_ue_re)
            else:
                pass

            vector = np.zeros((1,size))
            for j in range(size):
                vector[0][j] = auxiliar_sets[j]

            sets_matrix[i] = vector

        biggest_sum_rate = 0
        best_set_rates = []
        for i in sets_matrix[0]:
            soma = 0

            for j in sets_matrix[0]:
                if j != i:
                    soma = self.__channels[int(j)] @ self.__channels[int(j)].T

            plus = soma + np.eye(nc)

            sinr = (self.__channels[int(i)] @ np.linalg.inv(plus) @ self.__channels[int(i)].T)

            capacity = bandwidth * np.log2(1 + sinr)


            best_set_rates.append(capacity/1e6)

            biggest_sum_rate += capacity/1e6

        best_set = sets_matrix[0]

        for i in range(1, sets_number, 1):

            lista = []
            sum_rate_setx = 0
            for j in sets_matrix[i]:

                soma = 0

                for z in sets_matrix[i]:
                    if z != j:
                        soma += self.__channels[int(z)] @ self.__channels[int(z)].T

                plus = soma + np.eye(nc)

                sinr = self.__channels[int(j)] @ np.linalg.inv(plus) @ self.__channels[int(j)].T

                capacity = bandwidth * np.log2(1 + sinr)

                lista.append(capacity/1e6)
                #lista.append(lin2db(sinr))


                sum_rate_setx += capacity/1e6

            if sum_rate_setx > biggest_sum_rate:
                biggest_sum_rate = sum_rate_setx
                best_set = sets_matrix[i]
                best_set_rates = lista


        return best_set_rates


    def max_schedule(self):

        k = len(self.__users)

        L = len(self.__aps)


        ues_capacity = []

        for i in range(k):

            soma = 0
            for j in range(k):
                soma += self.__channels[j] @ self.__channels[j].T


            plus = soma + np.eye(L)

            sinr = self.__channels[i] @ np.linalg.inv(plus) @ self.__channels[i].T

            capacity = bandwidth * np.log2(1 + sinr)

            ues_capacity.append(capacity/10**6)


        ues_scheduled = []
        c = 0
        while c < L:
            best_ue = 0
            capacity_compare = 0
            for i in ues_capacity:
                if i > capacity_compare:
                    capacity_compare = i
                    best_ue = ues_capacity.index(i)

            ues_scheduled.append(best_ue)
            ues_capacity[best_ue] = 0

            c += 1

        ues_scheduled_rate = []
        for i in ues_scheduled:

            soma = 0

            for j in ues_scheduled:
                soma += self.__channels[j] @ self.__channels[j].T

            plus = soma + np.eye(L)

            sinr = self.__channels[i] @ np.linalg.inv(plus) @ self.__channels[i].T

            capacity = bandwidth * np.log2(1 + sinr)

            ues_scheduled_rate.append(capacity/10**6)

        return ues_scheduled_rate



















        #users_rates = []


        #return best_set_rates

































































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








