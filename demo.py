# coding=UTF-8
import time

import pulp
import os
import configparser


class lpsolver:
    def __init__(self, ini_path="config.ini"):
        self.weight_of_handle = 99999
        self.weight_of_save = 99999
        self.weight_of_trans = 99999

        self.cloud_compute_capacity = -9999

        self.pertime_plane_task = []
        self.pertime_plane_capacity = []
        self.total_task_time = []
        self.start_time_point = []

        self.time_upbound = 0
        self.ini_section = []
        if self.read_config(ini_path):
            print("读取文件成功")
            self.plane_amount = len(self.ini_section)
        else:
            print("读取文件失败")
        #####################################

    def read_config(self, config_path):
        config = configparser.ConfigParser()
        config.read(config_path, encoding='UTF-8')

        self.weight_of_handle = config.getint('task', 'weight_of_handle')
        self.weight_of_save = config.getint('task', 'weight_of_save')
        self.weight_of_trans = config.getint('task', 'weight_of_trans')

        self.cloud_compute_capacity = config.getint('cloud_server', 'cloud_compute_capacity')

        sections_list = config.sections()[1:-1]
        self.ini_section = sections_list

        flag = 0
        for section in sections_list:
            pertime_plane_task = config.getint(section, "task_amount")
            pertime_plane_capacity = config.getint(section, "compute_capacity")
            total_task_time = config.getint(section, "total_task_time")
            start_time_point = config.getint(section, "start_time_point")
            self.pertime_plane_capacity.append(pertime_plane_capacity)
            self.pertime_plane_task.append(pertime_plane_task)
            self.total_task_time.append(total_task_time)
            self.start_time_point.append(start_time_point)
            flag += (pertime_plane_task * 6 * total_task_time) / (pertime_plane_capacity + self.cloud_compute_capacity) \
                    + start_time_point

        print("need   ", flag)
        if len(sections_list) != len(self.pertime_plane_task) \
                or len(self.pertime_plane_task) != len(self.pertime_plane_capacity) \
                or len(self.pertime_plane_task) != len(self.total_task_time):
            return False
        else:
            return True

    def time_upbound_calculate(self) -> None:
        self.time_upbound = 5

    def single_lp_solver(self, time_upbound: int):
        temp_hE = ['handleE_%s' % i for i in range(time_upbound + 1)]
        temp_sE = ['saveE_%s' % i for i in range(time_upbound + 1)]
        temp_tE = ['transmitE_%s' % i for i in range(time_upbound + 1)]
        temp_SE = ['beensavedE_%s' % i for i in range(time_upbound)]
        temp_HE = ['savegohandleE_%s' % i for i in range(time_upbound)]
        temp_TE = ['savegotransE_%s' % i for i in range(time_upbound)]
        temp_saveE = ['savetotalE_%s' % i for i in range(time_upbound + 1)]
        vars_hE = [[] for _ in range(self.plane_amount)]
        vars_sE = [[] for _ in range(self.plane_amount)]
        vars_tE = [[] for _ in range(self.plane_amount)]
        vars_SE = [[] for _ in range(self.plane_amount)]
        vars_HE = [[] for _ in range(self.plane_amount)]
        vars_TE = [[] for _ in range(self.plane_amount)]
        vars_saveE = [[] for _ in range(self.plane_amount)]
        for i in range(self.plane_amount):
            vars_hE[i] = []
            vars_sE[i] = []
            vars_tE[i] = []
            vars_SE[i] = []
            vars_HE[i] = []
            section = self.ini_section[i]
            for j in temp_hE:
                exec('{} = pulp.LpVariable({}{}{},lowBound = 0, cat={}{}{})' \
                     .format(section + '_' + j, "'", section + '_' + j, "'", "'", 'Integer', "'"))
                vars_hE[i].append(section + '_' + j)
            for j in temp_sE:
                exec('{} = pulp.LpVariable({}{}{},lowBound = 0, cat={}{}{})' \
                     .format(section + '_' + j, "'", section + '_' + j, "'", "'", 'Integer', "'"))
                vars_sE[i].append(section + '_' + j)
            for j in temp_tE:
                exec('{} = pulp.LpVariable({}{}{},lowBound = 0, cat={}{}{})' \
                     .format(section + '_' + j, "'", section + '_' + j, "'", "'", 'Integer', "'"))
                vars_tE[i].append(section + '_' + j)

            for j in temp_SE:
                exec('{} = pulp.LpVariable({}{}{},lowBound = 0, cat={}{}{})' \
                     .format(section + '_' + j, "'", section + '_' + j, "'", "'", 'Integer', "'"))
                vars_SE[i].append(section + '_' + j)
            for j in temp_HE:
                exec('{} = pulp.LpVariable({}{}{},lowBound = 0, cat={}{}{})' \
                     .format(section + '_' + j, "'", section + '_' + j, "'", "'", 'Integer', "'"))
                vars_HE[i].append(section + '_' + j)
            for j in temp_saveE:
                exec('{} = pulp.LpVariable({}{}{},lowBound = 0, cat={}{}{})' \
                     .format(section + '_' + j, "'", section + '_' + j, "'", "'", 'Integer', "'"))
                vars_saveE[i].append(section + '_' + j)
            for j in temp_TE:
                exec('{} = pulp.LpVariable({}{}{},lowBound = 0, cat={}{}{})' \
                     .format(section + '_' + j, "'", section + '_' + j, "'", "'", 'Integer', "'"))
                vars_TE[i].append(section + '_' + j)

        plane_task_amount = []
        for i in range(self.plane_amount):
            temp_task_amount = [0 for _ in range(time_upbound)]
            temp_task_amount[self.start_time_point[i] - 1:self.total_task_time[i] + self.start_time_point[i] - 1] = \
                [self.pertime_plane_task[i] for _ in range(self.total_task_time[i])]
            plane_task_amount.append(temp_task_amount)
        my_prob_lp = pulp.LpProblem("", sense=pulp.LpMaximize)
        my_prob_lp += eval(vars_tE[1][1])
        for i in range(self.plane_amount):
            for j in range(time_upbound):
                my_prob_lp += (plane_task_amount[i][j] ==
                               eval(vars_hE[i][j + 1]) + eval(vars_sE[i][j + 1]) + eval(vars_tE[i][j + 1]))

                my_prob_lp += (
                        eval(vars_saveE[i][j]) == eval(vars_HE[i][j]) + eval(vars_SE[i][j]) + eval(vars_TE[i][j]))

                my_prob_lp += (eval(vars_saveE[i][j + 1]) == eval(vars_sE[i][j + 1]) + eval(vars_SE[i][j]))

                my_prob_lp += (self.weight_of_handle * (
                        eval(vars_hE[i][j + 1]) + eval(vars_HE[i][j])) + self.weight_of_save *
                               eval(vars_sE[i][j + 1]) + self.weight_of_trans * (
                                       eval(vars_tE[i][j + 1]) + eval(vars_TE[i][j]))
                               <= self.pertime_plane_capacity[i])

            # my_prob_lp += (eval(vars_sE[i][-1]) == eval(vars_hE[i][-1]) + eval(vars_tE[i][-1]))
            # my_prob_lp += (self.weight_of_handle * eval(vars_hE[i][-1]) + self.weight_of_trans * eval(vars_tE[i][-1])
            #                <= self.pertime_plane_capacity[i])
            my_prob_lp += (eval(vars_sE[i][0]) == 0)
            my_prob_lp += (eval(vars_hE[i][0]) == 0)
            my_prob_lp += (eval(vars_tE[i][0]) == 0)

            my_prob_lp += (eval(vars_SE[i][-1]) == 0)
            my_prob_lp += (eval(vars_sE[i][-1]) == 0)
            my_prob_lp += (eval(vars_saveE[i][-1]) == 0)
        # *              ***********                 *
        # my_prob_lp += (plane1_task_amount == hE_1 + sE_1 + tE_1)
        # my_prob_lp += (plane1_task_amount + sE_1 == hE_2 + sE_2 + tE_2)
        # my_prob_lp += (plane1_task_amount + sE_2 == hE_3 + sE_3 + tE_3)
        # my_prob_lp += (plane1_task_amount + sE_3 == hE_4 + sE_4 + tE_4)
        # my_prob_lp += (sE_4 == hE_5 + tE_5)
        #
        # my_prob_lp += (weight_of_handle * hE_1 + weight_of_save * sE_1 + weight_of_trans * tE_1 <= plane1_compute_capacity)
        # my_prob_lp += (weight_of_handle * hE_2 + weight_of_save * sE_2 + weight_of_trans * tE_2 <= plane1_compute_capacity)
        # my_prob_lp += (weight_of_handle * hE_3 + weight_of_save * sE_3 + weight_of_trans * tE_3 <= plane1_compute_capacity)
        # my_prob_lp += (weight_of_handle * hE_4 + weight_of_save * sE_4 + weight_of_trans * tE_4 <= plane1_compute_capacity)
        # my_prob_lp += (weight_of_handle * hE_5 + weight_of_trans * tE_5 <= plane1_compute_capacity)
        # *              ***********                 *

        # my_prob_lp += (plane2_task_amount == he_1 + se_1 + te_1)
        # my_prob_lp += (plane2_task_amount + se_1 == he_2 + se_2 + te_2)
        #
        # my_prob_lp += (plane2_task_amount + se_2 == he_3 + te_3)
        #
        # my_prob_lp += (weight_of_handle * he_1 + weight_of_save * se_1 + weight_of_trans * te_1 <= plane2_compute_capacity)
        # my_prob_lp += (weight_of_handle * he_2 + weight_of_save * se_2 + weight_of_trans * te_2 <= plane2_compute_capacity)
        # my_prob_lp += (weight_of_handle * he_3 + weight_of_trans * te_3 <= plane2_compute_capacity)
        # *              ***********                 *
        vars_Cc = ['Cc_%s' % i for i in range(time_upbound + 1)]
        vars_Sc = ['Sc_%s' % i for i in range(time_upbound + 1)]
        vars_saveC = ['savetotal_%s' % i for i in range(time_upbound + 1)]
        vars_sC = ['beensaved_%s' % i for i in range(time_upbound)]
        vars_hC = ['savegohandle_%s' % i for i in range(time_upbound)]

        for i in vars_Cc:
            exec('{} = pulp.LpVariable({}{}{},lowBound = 0, cat={}{}{})'.format(i, "'", i, "'", "'", 'Integer', "'"))
        for i in vars_Sc:
            exec('{} = pulp.LpVariable({}{}{},lowBound = 0, cat={}{}{})'.format(i, "'", i, "'", "'", 'Integer', "'"))
        for i in vars_saveC:
            exec('{} = pulp.LpVariable({}{}{},lowBound = 0, cat={}{}{})'.format(i, "'", i, "'", "'", 'Integer', "'"))
        for i in vars_sC:
            exec('{} = pulp.LpVariable({}{}{},lowBound = 0, cat={}{}{})'.format(i, "'", i, "'", "'", 'Integer', "'"))
        for i in vars_hC:
            exec('{} = pulp.LpVariable({}{}{},lowBound = 0, cat={}{}{})'.format(i, "'", i, "'", "'", 'Integer', "'"))

        for i in range(time_upbound):
            temp = None
            for j in range(self.plane_amount):
                temp += (eval(vars_tE[j][i + 1]) + eval(vars_TE[j][i]))
            my_prob_lp += (temp == eval(vars_Cc[i + 1]) + eval(vars_Sc[i + 1]))
            my_prob_lp += (eval(vars_saveC[i]) == eval(vars_hC[i]) + eval(vars_sC[i]))
            my_prob_lp += (eval(vars_saveC[i + 1]) == eval(vars_Sc[i + 1]) + eval(vars_sC[i]))

            my_prob_lp += (
                    (self.weight_of_handle * (eval(vars_Cc[i + 1]) + eval(vars_hC[i])) + self.weight_of_save * eval(
                        vars_Sc[i + 1])) <= self.cloud_compute_capacity)
        temp = None
        for j in range(self.plane_amount):
            temp += eval(vars_tE[j][-1])
        my_prob_lp += (temp + eval(vars_Sc[-1]) == eval(vars_Cc[-1]))
        my_prob_lp += (self.weight_of_handle * eval(vars_Cc[-1]) <= self.cloud_compute_capacity)
        my_prob_lp += (eval(vars_Sc[0]) == 0)
        my_prob_lp += (eval(vars_Cc[0]) == 0)
        my_prob_lp += (eval(vars_saveC[0]) == 0)

        my_prob_lp += (eval(vars_Sc[-1]) == 0)
        my_prob_lp += (eval(vars_sC[-1]) == 0)

        # print(my_prob_lp)
        my_prob_lp.solve()
        # for variable in my_prob_lp.variables():
        #     print("{} = {}".format(variable.name, variable.varValue))
        if pulp.LpStatus[my_prob_lp.status] != 'Infeasible':
            print(time_upbound, " can be solved ::", pulp.LpStatus[my_prob_lp.status])
            return True
        else:
            print(pulp.LpStatus[my_prob_lp.status])
            print(time_upbound, " cannot be solved")
            return False

    def muti_lp_solver(self, lowbound, upbound):
        mid = lowbound + ((upbound - lowbound) >> 1)
        print("mid  ", mid)
        if upbound < lowbound:
            print("optional ",self.last_mid)
            return self.last_mid

        if self.single_lp_solver(mid):
            self.last_mid = mid
            return self.muti_lp_solver(lowbound, mid - 1)
        else:
            return self.muti_lp_solver(mid + 1, upbound)

        # print("S:", pulp.LpStatus[my_prob_lp.status])
        # for i in my_prob_lp.variables():
        #     print(i.name, " ", i.varValue)
        # print("opt: ", pulp.value(my_prob_lp.objective))


# my_prob_lp += (tE_1 == Cc_1 + Sc_1)
# my_prob_lp += (tE_2 + Sc_1 == Cc_2 + Sc_2)
# my_prob_lp += (tE_3 + te_1 + Sc_2 == Cc_3 + Sc_3)
# my_prob_lp += (tE_4 + te_2 + Sc_3 == Cc_4 + Sc_4)
# my_prob_lp += (Sc_4 + te_3 + tE_5 == Cc_5)
#
# my_prob_lp += (weight_of_handle * Cc_1 + weight_of_save * Sc_1 <= cloud_compute_capacity)
# my_prob_lp += (weight_of_handle * Cc_2 + weight_of_save * Sc_2 <= cloud_compute_capacity)
# my_prob_lp += (weight_of_handle * Cc_3 + weight_of_save * Sc_3 <= cloud_compute_capacity)
# my_prob_lp += (weight_of_handle * Cc_4 + weight_of_save * Sc_4 <= cloud_compute_capacity)
# my_prob_lp += (weight_of_handle * Cc_5 <= cloud_compute_capacity)
a = time.time()
lpsolver = lpsolver("test_ini.ini")
lpsolver.single_lp_solver(350)
#lpsolver.muti_lp_solver(5, 500)
b = time.time()
print(a)
print(b)
print(b - a)
