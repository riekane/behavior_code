from shuler_behavior import box_functions, timescapes
import time
import numpy as np
import random


def check_rate(task_shell, port):
    block = int((time.time() - task_shell.task_start_time) //
                (task_shell.max_time / len(port.dist_info['rates'])))
    block = len(port.dist_info['rates']) - 1 if block >= len(port.dist_info['rates']) else block
    return port.dist_info['rates'][block]


def blocked_give_up_task(exp_port, bg_port, session_manager):
    step_size = .1
    rates = [.4, .8, .4, .8, .4, .8]

    if np.random.random() > .5:
        rates.reverse()
    blocks = np.unique(rates)
    blocks.sort()

    start = False
    background_start_time = time.time()
    background_time = 0
    background_rewards = 0
    exp_start_time = None
    trial_start_time = None
    exp_available = False
    exp_taken = False
    bin_num = 0
    background_available = True
    forced = False
    choice = 'free'

    # This loops until all the trials are complete
    while task_shell.condition():
        for port in task_shell.ports:
            if port.dist_info['distribution'] == timescapes.exp_decreasing:
                port.available = exp_available or exp_taken
            elif port.dist_info['distribution'] == 'background':
                port.available = background_available or exp_taken

        task_shell.sol_cleanup()
        task_shell.led_cleanup()
        task_shell.check_time()  # print out the current time and number of trials and rewards

        # This controls the task flow as the mouse moves in and out of ports
        for port in task_shell.ports:
            for change, event in zip([port.head_status_change(), port.lick_status_change()], ['head', 'lick']):
                if change == 1:  # beam break
                    if start:
                        task_shell.log(port.name, 1, event)  # Log the event
                    if event == 'head':
                        if port.dist_info['distribution'] == timescapes.exp_decreasing and exp_available:
                            print(choice)
                            task_shell.log(port.name, 1, choice)
                            exp_available = False
                            exp_taken = True
                            forced = False
                            exp_start_time = time.time()
                            bin_num = 0
                            task_shell.port_dict['background'].led_stay = False
                            task_shell.led_cleanup()
                        elif port.dist_info['distribution'] == 'background':
                            background_start_time = time.time()
                            if not start:
                                task_shell.start()
                                task_shell.trial_number = 1
                                task_shell.start_trial(port_name=port.name)
                                start = True
                                trial_start_time = time.time()
                                task_shell.log(port.name, 1, event)  # Log the event
                                print('starting task...')
                            if exp_taken:
                                background_available = True
                                exp_taken = False
                                background_start_time = time.time()
                                trial_start_time = time.time()
                                background_time = 0
                                background_rewards = 0
                                task_shell.phase = check_rate(task_shell, port)
                                print('returned to background')
                    elif event == 'lick':
                        port.licked = True
                elif change == -1:  # beam un-break
                    if start:
                        task_shell.log(port.name, 0, event)  # Log the event
                    if port.dist_info['distribution'] == 'background' and event == 'head':
                        background_time += time.time() - background_start_time

        # This controls reward delivery
        if start:
            for port in task_shell.ports:
                if port.dist_info['distribution'] == 'background' and port.head_status == 1 and background_available:
                    current_time = time.time()
                    # block = int((current_time - task_shell.task_start_time) //
                    #             (task_shell.max_time / len(port.dist_info['rates'])))
                    # if block >= len(port.dist_info['rates']):
                    #     block = len(port.dist_info['rates']) - 1
                    interval = 1 / task_shell.phase
                    if (background_time + current_time - background_start_time) // interval > background_rewards:
                        if port.licked:
                            port.sol_on()
                            task_shell.log(port.name, 1, 'reward')
                            task_shell.reward_count += 1
                            print(
                                f'background reward delivered: {background_time + time.time() - background_start_time}'
                                f' / {time.time() - trial_start_time}')
                            port.licked = False
                        else:
                            print(f'background reward missed: {background_time + time.time() - background_start_time}'
                                  f' / {time.time() - trial_start_time}')
                            task_shell.log(port.name, 1, 'missed_reward')
                        background_rewards += 1
                    if background_time + current_time - background_start_time > port.dist_info['duration']:
                        print('exp option available')
                        # port.led_on()
                        # task_shell.log(port.name, 1, 'LED')
                        background_time = 0
                        background_rewards = 0
                        background_start_time = time.time()
                        trial_start_time = time.time()
                        task_shell.next_trial(end_port_name=port.name, start_port_name=port.name)
                        if task_shell.phase == blocks[1] or forced:
                            exp_available = True
                            background_available = False
                            task_shell.log(port.name, 1, 'forced_switch')
                            print('forced switch')
                            choice = 'forced'
                        else:
                            forced = True

                if port.dist_info['distribution'] == timescapes.exp_decreasing:
                    if exp_taken and (time.time() - exp_start_time) // step_size > bin_num:
                        bin_num += 1
                        if port.head_status == 1 and port.licked:
                            density_function = port.dist_info['distribution']
                            prob = density_function(time.time() - exp_start_time,
                                                    cumulative=port.dist_info['cumulative'],
                                                    starting=port.dist_info['starting_probability']) * step_size
                            task_shell.log(port.name, prob, 'probability')
                            # print_string = 'port ' + str(port.name) + ' P(reward) = ' + str(prob)
                            print_string = f'port {port.name} P(reward) = {prob}'
                            # print(random.random())
                            if prob > random.random():
                                port.sol_on()
                                port.licked = False
                                task_shell.log(port.name, 1, 'reward')
                                print(print_string + ' (rewarded)')
                                task_shell.reward_count += 1


def main():
    exp_port = box_functions.Port({
        'name': 'exp_port',
        'solenoid_calibration': .01,
        'solenoid_pin': 9,
        'led_pins': [4],
        'ir_pins': [27, 17],
        'port_number': 1
    })
    bg_port = box_functions.Port({
        'name': 'bg_port',
        'solenoid_calibration': .01,
        'solenoid_pin': 11,
        'led_pins': [18],
        'ir_pins': [24, 23],
        'port_number': 2
    })
    session_manager = box_functions.SessionManager(mouse='testmouse')
    blocked_give_up_task(exp_port, bg_port, session_manager)
    # box.run_gui(mouse_list=['ES024', 'ES025', 'ES026', 'testmouse'])


if __name__ == '__main__':
    main()
