import time
import RPi.GPIO as GPIO
import datetime
import os
from timescapes import *
# import pexpect
import pickle
import tempfile
# import smbus
import numpy as np


class Port:
    def __init__(self, port_info):
        self.name = port_info.name
        self.port_info = port_info

        if 'solenoid_calibration' in port_info.keys:
            self.sol_cal = port_info['solenoid_calibration']
            if self.sol_cal.dtype == float:
                self.sol_duration = self.sol_cal
            elif self.sol_cal.dtype == str:
                with open(self.sol_cal, 'rb') as f:
                    durations = pickle.load(f)
                self.sol_duration = durations[port_info['port_number']]
        if 'solenoid_pin' in port_info.keys:
            self.solenoid_pin = port_info['solenoid_pin']
            GPIO.setup(self.solenoid_pin, GPIO.OUT)
            GPIO.output(self.solenoid_pin, GPIO.LOW)
            self.sol = False
            self.sol_opened_time = None
        if 'led_pins' in port_info.keys:
            self.led_pins = port_info['led_pins']
            if self.led_pins.dtype == int:
                self.led_pins = [self.led_pins]
            self.led = []
            for pin in self.led_pins:
                GPIO.setup(pin, GPIO.OUT)
                GPIO.output(pin, GPIO.LOW)
                self.led.append(False)
        if 'ir_pins' in port_info.keys:
            self.ir_pins = port_info['ir_pins']
            if self.ir_pins.dtype == int:
                self.ir_pins = [self.ir_pins]
            for pin in self.ir_pins:
                GPIO.setup(pin, GPIO.IN)
                print(f'Port {self.name} IR status: {GPIO.input(pin)}')
            self.ir_status = np.zeros(len(self.ir_pins))
            self.ir_break_time = np.zeros(len(self.ir_pins))

    def sol_on(self):
        GPIO.output(self.solenoid_pin, GPIO.HIGH)
        self.sol = True
        self.sol_opened_time = time.time()
        return time.time()

    def sol_off(self):
        GPIO.output(self.solenoid_pin, GPIO.LOW)
        self.sol = False
        return time.time()

    def sol_cleanup(self):
        if self.sol and self.sol_opened_time + self.sol_duration < time.time():
            return self.sol_off() - self.sol_opened_time
        return False

    def led_on(self, led_num=0):
        GPIO.output(self.led_pins[led_num], GPIO.HIGH)
        self.led[led_num] = True
        print(f'led on {led_num}')
        return time.time()

    def led_off(self, led_num=0):
        GPIO.output(self.led_pins[led_num], GPIO.LOW)
        self.led[led_num] = False
        print(f'led off {led_num}')
        return time.time()

    def ir_status_change(self):
        changes = []
        for i, pin in enumerate(self.ir_pins):
            change = GPIO.input(pin) - self.ir_status[i]
            self.ir_status[i] += change
            changes.append(change)
        return changes


class SessionManager:
    def __init__(self, mouse='testmouse'):
        self.ip = '10.203.111.198'
        # self.ip = '10.203.138.100'
        # self.ip = '10.203.137.141'
        # error with 0: re.compile('[Pp]assword: ') means you need to update the ip address. open command prompt and
        # type ipconfig/all then press enter. Find the ip address starting with 10 and update it here
        self.user = 'Elissa'
        self.host_name = os.uname()[1]
        self.password = 'shuler'
        self.mouse = mouse
        self.data_write_path = "/data/" + self.mouse
        self.datetime = time.strftime("%Y-%m-%d_%H-%M-%S")
        self.filename = "data_" + self.datetime + ".txt"
        self.ssh_path = 'GoogleDrive/Code/Python/behavior_code/data/' + self.mouse
        self.data_send_path = 'C:/Users/Elissa/' + self.ssh_path + '/'
        self.halted = False
        self.smooth_finish = False
        GPIO.setmode(GPIO.BCM)
        print(os.getcwd())
        os.system('sudo -u pi mkdir -p ' + os.getcwd() + self.data_write_path)
        os.chdir(os.getcwd() + self.data_write_path)
        os.system('sudo touch ' + self.filename)
        os.system('sudo chmod o+w ' + self.filename)
        self.f = open(self.filename, 'w')
        self.start_time = None
        self.sync_pins = {'session': 25,
                          'task': 8,
                          'trial': 7,
                          'head1': 16,
                          'head2': 20,
                          'lick1': 21,
                          'lick2': 5,
                          'sol1': 6,
                          'sol2': 13}

    def start(self, task_list):
        for val in self.sync_pins.values():
            GPIO.setup(val, GPIO.OUT)
            GPIO.output(val, GPIO.LOW)

        info_fields = 'mouse,date,time,task,port1_info,port2_info,box'
        data_fields = 'session_time,task,task_time,trial,trial_time,phase,port,value,key'

        self.f.write(info_fields + '\n')
        for task in task_list:
            info = [self.mouse, self.datetime[0:10], self.datetime[11:19], task.name]
            for port in task.ports:
                info = info + [str(port.dist_info)]
            info.append(self.host_name)
            info_string = ','.join(info)
            self.f.write(info_string + '\n')
        self.f.write('\n'.join(['# Data', data_fields, '']))

        self.start_time = time.time()
        GPIO.output(self.sync_pins['session'], GPIO.HIGH)
        self.log('nan,nan,nan,nan,setup,nan,1,session')
        for task in task_list:
            perform(task)

    def log(self, string):  # Adds session time stamp to beginning of string and logs it
        session_time = time.time() - self.start_time
        new_line = str(session_time) + ',' + string + '\n'
        # print(new_line)
        self.f.write(new_line)

    def end(self):
        GPIO.output(self.sync_pins['session'], GPIO.LOW)
        self.log('nan,nan,nan,nan,setup,nan,0,session')
        self.f.close()
        os.system('sudo chmod o-w ' + self.filename)
        mkdir_command = 'if not exist %s mkdir %s' % (
            self.ssh_path.replace('/', '\\'), self.ssh_path.replace('/', '\\'))
        ssh(self.ip, mkdir_command, self.user, self.password)
        if not scp(self.ip, self.filename, self.data_send_path, self.user, self.password):
            print('\nSuccessful file transfer to "%s"\nDeleting local file from pi.' % self.data_send_path)
            os.remove(self.filename)
        else:
            print('connection back to desktop timed out')
        GPIO.cleanup()
        os.chdir(os.path.join(os.getcwd(), '..', '..'))
        print('\nFile closed and clean up complete')
        if self.halted:
            print('Session stopped early via KeyboardInterrupt')
        elif self.smooth_finish:
            print('Session ran smoothly to the end')
        else:
            print('Session ended due to an error:\n')

#
#
#
# def run(mouse_name, task_structure):
#     pass
#
#
# class Box:
#     def __init__(self):
#         pass
#
#
# class Task:
#     def __init__(self, session, name='blank', structure=None, ports=None, limit='trials',
#                  maximum=None, forgo=True, forced_trials=False):
#         print('Starting task: %s' % name)
#         self.structure = structure
#         self.port_dict = ports
#         self.ports = ports.values()
#         # self.ports = initialize_ports(ports, distributions)
#         self.session = session
#         self.name = name
#         self.limit = limit
#         if limit == 'trials':
#             self.num_trials = maximum if maximum else global_num_trials
#             self.max_time = None
#         elif limit == 'time':
#             self.max_time = maximum * 60 if maximum else global_max_time * 60
#             self.num_trials = None
#         self.trial_number = 'nan'
#         self.phase = 'setup'
#         self.task_start_time = None
#         self.trial_start_time = None
#         self.last_video_start = None
#         self.reward_count = 0
#         self.last_report = 0
#         self.report_interval = 5  # Seconds
#         self.forgo = forgo
#         self.forced_trials = forced_trials
#
#     def initialize(self):
#         self.task_start_time = time.time()
#         for port in self.ports:
#             port.head_status = GPIO.input(port.ir_head_pin)
#             port.lick_status = GPIO.input(port.ir_lick_pin)
#
#     def start(self):
#         self.task_start_time = time.time()
#         self.log('nan', 1, 'task')
#         self.trial_start_time = time.time()
#         self.trial_number = 0
#         # self.check_video()
#
#     def end(self):
#         self.phase = 'setup'
#         self.trial_number = 'nan'
#         self.sol_cleanup()
#         self.log('nan', 0, 'task')
#
#     def interrupted(self):
#         self.log('nan', 0, 'task_interrupted')
#
#     def log(self, port_name, start, key):  # Adds task name and timestamp, trial name and timestamp, and phase
#         task_timestamp = time.time() - self.task_start_time
#         if self.trial_number == 'nan':
#             trial_timestamp = 'nan'
#         else:
#             trial_timestamp = time.time() - self.trial_start_time
#         new_string = ','.join(
#             [self.name, str(task_timestamp),
#              str(self.trial_number), str(trial_timestamp),
#              str(self.phase), str(port_name), str(start), key])
#         if key in ['task', 'trial']:
#             if start:
#                 GPIO.output(self.session.sync_pins[key], GPIO.HIGH)
#             else:
#                 GPIO.output(self.session.sync_pins[key], GPIO.LOW)
#         elif key in ['head', 'lick']:
#             if start:
#                 GPIO.output(self.session.sync_pins[key + str(port_name)], GPIO.HIGH)
#             else:
#                 GPIO.output(self.session.sync_pins[key + str(port_name)], GPIO.LOW)
#                 if key == 'head':
#                     GPIO.output(self.session.sync_pins['trial'], GPIO.LOW)
#         elif key == 'reward':
#             GPIO.output(self.session.sync_pins['sol' + str(port_name)], GPIO.HIGH)
#         elif key == 'sol_duration':
#             GPIO.output(self.session.sync_pins['sol' + str(port_name)], GPIO.LOW)
#         self.session.log(new_string)
#
#     def start_trial(self, port_name='nan'):
#         self.trial_start_time = time.time()
#         self.log(port_name, 1, 'trial')
#         current_time = (time.time() - self.task_start_time) / 60
#         print('trial %i start at %f' % (self.trial_number, current_time))
#         # print('time: %f' % current_time)
#
#     def end_trial(self, port_name='nan'):
#         self.log(port_name, 0, 'trial')
#         self.trial_number += 1
#
#     def next_trial(self, end_port_name='nan', start_port_name='nan'):
#         self.end_trial(port_name=end_port_name)
#         if self.condition():
#             self.start_trial(port_name=start_port_name)
#
#     def sol_cleanup(self):
#         for port in self.ports:
#             closed = port.sol_cleanup()
#             if closed:
#                 self.log(port.name, 0, 'reward')
#
#     def led_cleanup(self):
#         for port in self.ports:
#             if port.available == port.led:
#                 if port.available:
#                     port.led_off()
#                     self.log(port.name, 0, 'LED')
#                 else:
#                     port.led_on()
#                     self.log(port.name, 1, 'LED')
#
#     def check_buttons(self, button_pad):
#         button_presses = button_pad.presses()
#         if 1 in button_presses[0:len(self.ports)]:
#             index = button_presses.index(1)
#             self.ports[index].sol_on()
#             time.sleep(self.ports[index].base_duration)
#             self.ports[index].sol_off()
#             print('manual reward delivered in port  ' + str(index))
#             self.log(self.ports[index].name, 1, 'manual_reward')
#
#     def condition(self):
#         if self.limit == 'trials':
#             conditional = self.trial_number <= self.num_trials
#         elif self.limit == 'time':
#             conditional = time.time() - self.task_start_time < self.max_time
#         else:
#             conditional = False
#         return conditional
#
#     def check_video(self):
#         minutes_per = 5
#         if not self.last_video_start or time.time() - self.last_video_start > minutes_per * 60:
#             print('video recording started')
#             self.last_video_start = time.time()
#             os.system(
#                 'ssh Elissa@10.194.169.93 \'Anaconda3\\Scripts\\activate open_cv && cd PycharmProjects\\open_cv_test && curl -X POST -H "Content-Type: application/json" -d "{\\"mouse\\":\\"' + self.session.mouse + '\\"}" localhost:8000/check_start\'')
#             self.log('nan', 1, 'video')
#
#     def check_time(self):
#         if (time.time() - self.last_report) > self.report_interval:
#             task_time = time.time() - self.task_start_time
#             # print('%i rewards in %im %is' % (
#             #     int(self.reward_count), int(task_time // 60), int(task_time % 60)))
#             print('%i rewards in %s' % (
#                 int(self.reward_count), str(datetime.timedelta(seconds=task_time))[2:7]))
#             self.last_report = time.time()
