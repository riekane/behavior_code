import random
import time
from support_classes import ButtonPad
from timescapes import *


def give_up_task(task_shell, step_size=.1):
    num_ports = 2  # The number of ports used in the task, do not change
    task_shell.check_number_of_ports(num_ports)
    button_pad = ButtonPad()

    current_port = None
    previous_reward_check = 0
    licked = True

    # This loops until all the trials are complete
    while task_shell.condition():
        # task_shell.check_buttons(button_pad)
        task_shell.sol_cleanup()
        task_shell.check_time()

        # This controls the task flow as the mouse moves in and out of ports
        for port in task_shell.ports:
            for change, event in zip([port.head_status_change(), port.lick_status_change()], ['head', 'lick']):
                if change == 1:
                    if event == 'head':
                        task_shell.phase = 'consume'
                        print(str(time.time() - task_shell.task_start_time) + ' port ' + str(port.name) + ' entry')
                        if not current_port:
                            task_shell.trial_number = 1
                            task_shell.start_trial()
                        elif port.name != current_port:
                            task_shell.next_trial(end_port_name=current_port, start_port_name=port.name)
                            if not task_shell.condition():
                                licked = False
                                break
                            previous_reward_check = 0
                            licked = True
                        current_port = port.name
                    if event == 'lick':
                        licked = True
                        # print('lick start')
                    task_shell.log(port.name, 1, event)
                elif change == -1:
                    if event == 'head':
                        task_shell.phase = 'transit'
                    # elif event == 'lick':
                    # print('lick stop')
                    task_shell.log(port.name, 0, event)

        # This controls reward delivery
        for port in task_shell.ports:
            if port.head_status == 1 and licked:
                trial_time = time.time() - task_shell.trial_start_time
                if trial_time > previous_reward_check + step_size:
                    previous_reward_check = trial_time
                    density_function = port.dist_info['distribution']
                    prob = density_function(trial_time, port.dist_info['cumulative'],
                                            port.dist_info['peak_time']) * step_size
                    # prob = port.get_prob(trial_time) * step_size
                    task_shell.log(port.name, prob, 'probability')
                    print_string = 'port ' + str(port.name) + ' P(reward) = ' + str(prob)
                    if prob > random.random():
                        port.sol_on()
                        licked = False
                        task_shell.log(port.name, 1, 'reward')
                        print(print_string + ' (rewarded)')
                        task_shell.reward_count += 1
                    # else:
                    #     print(print_string + ' (not)')


def give_up_forgo_task(task_shell, step_size=.1):
    num_ports = 2  # The number of ports used in the task, do not change
    task_shell.check_number_of_ports(num_ports)

    current_port = None
    previous_reward_check = 0
    licked = True
    fixed_port_rewarded = False

    # This loops until all the trials are complete
    while task_shell.condition():
        task_shell.sol_cleanup()
        task_shell.check_time()

        # This controls the task flow as the mouse moves in and out of ports
        for port in task_shell.ports:
            for change, event in zip([port.head_status_change(), port.lick_status_change()], ['head', 'lick']):
                if change == 1:
                    if event == 'head':
                        task_shell.phase = 'consume'
                        print(str(time.time() - task_shell.task_start_time) + ' port ' + str(port.name) + ' entry')
                        if not current_port:
                            task_shell.trial_number = 1
                            task_shell.start_trial(port_name=port.name)
                        elif port.name != current_port:
                            task_shell.next_trial(end_port_name=current_port, start_port_name=port.name)
                            if not task_shell.condition():
                                licked = False
                                break
                            previous_reward_check = 0
                            licked = True
                            fixed_port_rewarded = False
                        current_port = port.name
                    if event == 'lick':
                        licked = True
                        # print('lick start')
                    task_shell.log(port.name, 1, event)
                elif change == -1:
                    if event == 'head':
                        task_shell.phase = 'transit'
                    # if event == 'lick':
                    #     print('lick stop')
                    task_shell.log(port.name, 0, event)

        # This controls reward delivery
        for port in task_shell.ports:
            if port.name == current_port:
                if port.distribution == fixed_single:
                    if port.head_status == 1:
                        phase = int((time.time() - task_shell.task_start_time) //
                                    (task_shell.max_time / len(port.dist_args)))
                        if not task_shell.condition():
                            break
                        wait_time = port.dist_args[phase]
                        trial_time = time.time() - task_shell.trial_start_time
                        if trial_time > wait_time and not fixed_port_rewarded:
                            port.sol_on()
                            task_shell.log(port.name, 1, 'reward')
                            print('trial: %i port: %i fixed reward at %f seconds' % (
                                task_shell.trial_number, port.name, trial_time))
                            fixed_port_rewarded = True
                            task_shell.reward_count += 1
                elif port.distribution == exp_decreasing:
                    if port.head_status == 1 and licked:
                        trial_time = time.time() - task_shell.trial_start_time
                        if trial_time > previous_reward_check + step_size:
                            previous_reward_check = trial_time
                            prob = port.get_prob(trial_time) * step_size
                            task_shell.log(port.name, prob, 'probability')
                            print_string = 'port ' + str(port.name) + ' P(reward) = ' + str(prob)
                            if prob > random.random():
                                port.sol_on()
                                licked = False
                                task_shell.log(port.name, 1, 'reward')
                                print(print_string + ' (rewarded)')
                                task_shell.reward_count += 1


def training_cued_forgo_task(task_shell, step_size=.1):
    num_ports = 2  # The number of ports used in the task, do not change
    task_shell.check_number_of_ports(num_ports)

    current_port = None
    previous_background_reward_time = None
    background_start_time = None
    licked = True

    # This loops until all the trials are complete
    while task_shell.condition():
        task_shell.sol_cleanup()  # close open solenoids if their duration is passed
        task_shell.check_time()  # print out the current time and number of trials and rewards

        # This controls the task flow as the mouse moves in and out of ports
        for port in task_shell.ports:
            for change, event in zip([port.head_status_change(), port.lick_status_change()], ['head', 'lick']):
                if change == 1:  # beam break
                    if event == 'head':  # head entry
                        if not current_port:  # Initialize the first trial
                            if port.dist_info['distribution'] == 'background':
                                task_shell.trial_number = 1
                                task_shell.start_trial(port_name=port.name)
                                previous_background_reward_time = time.time()
                        elif port.name != current_port:  # If port switch, reset for new trial
                            task_shell.next_trial(end_port_name=current_port, start_port_name=port.name)
                            previous_background_reward_time = time.time()
                        current_port = port.name  # set the current port
                    if event == 'lick':  # lick start
                        licked = True
                    task_shell.log(port.name, 1, event)  # Log the event
                elif change == -1:  # beam un-break
                    if event == 'head':  # head exit
                        pass
                    if event == 'lick':  # lick stop
                        pass
                    task_shell.log(port.name, 0, event)  # Log the event

        # # This controls reward delivery
        # for port in task_shell.ports:
        #     if port.name == current_port:
        #         if port.head_status == 1:
        #             if port.dist_info['distribution'] == 'background':
        #
        #             if reward_condition:
        #                 port.sol_on()
        #                 task_shell.log(port.name, 1, 'reward')


def cued_forgo_task(task_shell, step_size=1):
    num_ports = 2  # The number of ports used in the task, do not change
    task_shell.check_number_of_ports(num_ports)
    travel_time_limit = 1

    start = False
    background_start_time = None
    background_time = 0
    background_rewards = 0
    exp_start_time = None
    exp_available = False
    exp_taken = False
    bin_num = 0

    # This loops until all the trials are complete
    while task_shell.condition():
        task_shell.sol_cleanup()
        task_shell.led_cleanup()
        task_shell.check_time()  # print out the current time and number of trials and rewards

        # This controls the task flow as the mouse moves in and out of ports
        for port in task_shell.ports:
            for change, event in zip([port.head_status_change(), port.lick_status_change()], ['head', 'lick']):
                if change == 1:  # beam break
                    task_shell.log(port.name, 1, event)  # Log the event
                    if event == 'head':
                        if port.dist_info['distribution'] == exp_decreasing and exp_available:
                            exp_available = False
                            exp_taken = True
                            exp_start_time = time.time()
                            bin_num = 0
                            print('took exp option')
                        elif port.dist_info['distribution'] == 'background':
                            background_start_time = time.time()
                            if not start:
                                task_shell.trial_number = 1
                                task_shell.start_trial(port_name=port.name)
                                start = True
                                print('starting task...')
                            if exp_taken:
                                exp_taken = False
                                background_start_time = time.time()
                                background_time = 0
                                background_rewards = 0
                                print('returned to background')
                    elif event == 'lick':
                        port.licked = True
                elif change == -1:  # beam un-break
                    task_shell.log(port.name, 0, event)  # Log the event
                    if port.dist_info['distribution'] == 'background':
                        background_time += time.time() - background_start_time

        # This controls reward delivery
        if start:
            if exp_available and (time.time() - task_shell.trial_start_time) > travel_time_limit:
                exp_available = False
                print('skipped exp option')
            for port in task_shell.ports:
                if port.dist_info['distribution'] == 'background' and port.head_status == 1:
                    block = int((time.time() - task_shell.task_start_time) //
                                (task_shell.max_time / len(port.dist_info['rates'])))
                    if block >= len(port.dist_info['rates']):
                        block = len(port.dist_info['rates']) - 1
                    interval = 1 / port.dist_info['rates'][block]
                    if (background_time + time.time() - background_start_time) // interval > background_rewards:
                        if port.licked:
                            port.sol_on()
                            task_shell.log(port.name, 1, 'reward')
                            task_shell.reward_count += 1
                            print(
                                f'background reward delivered: {background_time + time.time() - background_start_time}')
                            port.licked = False
                        else:
                            print(f'background reward missed: {background_time + time.time() - background_start_time}')
                            task_shell.log(port.name, 1, 'missed_reward')
                        background_rewards += 1
                    if background_time + time.time() - background_start_time > port.dist_info['duration']:
                        print('exp option available')
                        port.led_on()
                        task_shell.log(port.name, 1, 'LED')
                        exp_available = True
                        background_time = 0
                        background_rewards = 0
                        background_start_time = time.time()
                        task_shell.next_trial(end_port_name=port.name, start_port_name=port.name)
                if port.dist_info['distribution'] == exp_decreasing:
                    if port.head_status == 1 and port.licked and exp_taken:
                        if (time.time() - exp_start_time) // step_size > bin_num:
                            bin_num += 1
                            density_function = port.dist_info['distribution']
                            prob = density_function(time.time() - exp_start_time,
                                                    cumulative=port.dist_info['cumulative'],
                                                    starting=port.dist_info['starting_probability']) * step_size
                            task_shell.log(port.name, prob, 'probability')
                            # print_string = 'port ' + str(port.name) + ' P(reward) = ' + str(prob)
                            print_string = f'port {port.name} P(reward) = {prob}'
                            print(random.random())
                            if prob > random.random():
                                port.sol_on()
                                port.licked = False
                                task_shell.log(port.name, 1, 'reward')
                                print(print_string + ' (rewarded)')
                                task_shell.reward_count += 1


def generic_task(task_shell, step_size=.1):
    num_ports = 2  # The number of ports used in the task, do not change
    task_shell.check_number_of_ports(num_ports)

    current_port = None

    # This loops until all the trials are complete
    while task_shell.condition():
        task_shell.sol_cleanup(
            [port.base_duration for port in task_shell.ports])  # close open solenoids if their duration is passed
        task_shell.check_time()  # print out the current time and number of trials and rewards

        # This controls the task flow as the mouse moves in and out of ports
        for port in task_shell.ports:
            for change, event in zip([port.head_status_change(), port.lick_status_change()], ['head', 'lick']):
                if change == 1:  # beam break
                    if event == 'head':  # head entry
                        if not current_port:  # Initialize the first trial
                            task_shell.trial_number = 1
                            task_shell.start_trial(port_name=port.name)
                        elif port.name != current_port:  # If port switch, reset for new trial
                            task_shell.next_trial(end_port_name=current_port, start_port_name=port.name)
                        current_port = port.name  # set the current port
                    if event == 'lick':  # lick start
                        pass
                    task_shell.log(port.name, 1, event)  # Log the event
                elif change == -1:  # beam un-break
                    if event == 'head':  # head exit
                        pass
                    if event == 'lick':  # lick stop
                        pass
                    task_shell.log(port.name, 0, event)  # Log the event

        reward_condition = False  # Place holder for writing in a condition using some distribution

        # This controls reward delivery
        for port in task_shell.ports:
            if port.name == current_port:
                if port.head_status == 1:
                    if reward_condition:
                        port.sol_on()
                        task_shell.log(port.name, 1, 'reward')
