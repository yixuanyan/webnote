# python3
import configparser
import random

plane_nums = 75
config = configparser.ConfigParser()
filename = 'test_ini_{}.ini'.format(plane_nums)
config = configparser.ConfigParser()
config.read(filename)
plane_name = []
for i in range(plane_nums):
    plane_name.append("plane{}".format(i + 1))
try:
    config.add_section('task')
    for i in plane_name:
        config.add_section(i)
    config.add_section("cloud_server")
except configparser.DuplicateSectionError:
    pass
config.set("task", "weight_of_handle", '6')
config.set("task", "weight_of_save", "3")
config.set("task", "weight_of_trans", "1")
for i in plane_name:
    task_amount = random.randint(30, 90)
    compute_capacity = int(task_amount * random.uniform(3, 4))
    start_time_point = random.randint(0, 200)
    total_task_time = random.randint(3, 9)
    config.set(i, "task_amount", str(task_amount))
    config.set(i, "compute_capacity",str(compute_capacity ))
    config.set(i, "start_time_point", str(start_time_point))
    config.set(i, "total_task_time",str(total_task_time ))
config.set("cloud_server", "cloud_compute_capacity", '300')
with open(filename, "w+") as config_file:
    config.write(config_file)
