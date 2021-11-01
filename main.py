from support_classes import *
from tasks import *
from timescapes import *
import random


def give_up(session, reward_level, peak_time, session_length):
    print(reward_level)
    print(peak_time)
    print(session_length)
    exp_dist = {'distribution': lin_over_ex,
                'cumulative': reward_level,
                'peak_time': peak_time}
    port_1 = Port(1, dist_info=exp_dist)
    port_2 = Port(2, dist_info=exp_dist)
    ports = [port_1, port_2]
    task1 = Task(session, name='give_up', structure=give_up_task, ports=ports, maximum=session_length, limit='time')
    session.start([task1])


def give_up_forgo(session, reward_level, starting_prob, session_length, fixed_times):
    print(reward_level)
    print(starting_prob)
    print(session_length)
    exp_dist = {'distribution': exp_decreasing,
                'cumulative': reward_level,
                'staring_probability': starting_prob}
    background_dist = {'distribution': fixed_single,
                       'delays': fixed_times}
    dists = [exp_dist, background_dist]
    # dists = [background_dist, exp_dist]
    port_1 = Port(1, dist_info=dists[0])
    port_2 = Port(2, dist_info=dists[1])
    task1 = Task(session, name='give_up_forgo', structure=give_up_forgo_task, ports=[port_1, port_2],
                 maximum=session_length, limit='time')
    session.start([task1])


def cued_forgo(session, reward_level, starting_prob, session_length, training=False):
    print(reward_level)
    print(starting_prob)
    print(session_length)
    exp_dist = {'distribution': exp_decreasing,
                'cumulative': reward_level,
                'starting_probability': starting_prob}
    rates = [1, .8, .6, .4, .2]
    random.shuffle(rates)
    background_dist = {'distribution': 'background',
                       'rates': rates,
                       'duration': 10}
    print(background_dist['rates'])
    dists = [exp_dist, background_dist]
    # dists = [background_dist, exp_dist]
    port_1 = Port(1, dist_info=dists[0])
    port_2 = Port(2, dist_info=dists[1])
    # port_1 = Port(1, distribution=exp_decreasing, dist_args=[reward_level, starting_prob])
    # port_2 = Port(2, distribution='background', dist_args=[[1, .8, .6, .4, .2], 10])
    task1 = Task(session, name='cued_forgo', structure=cued_forgo_task, ports=[port_1, port_2],
                 maximum=session_length, limit='time')
    session.start([task1])


def main(mouse, to_run):
    mouse_settings = {
        'testmouse': [5, 1, 10],
        'ES011': [5, 1, 10],  # reward level, starting prop, session time, [intervals].
        'ES012': [5, 1, 10],  # reward level, starting prop, session time, [intervals].
        'ES013': [5, 1, 10],  # reward level, starting prop, session time, [intervals].
        'ES014': [5, 1, 10],  # reward level, starting prop, session time, [intervals].
    }

    if mouse not in mouse_settings.keys():
        raise MouseSettingsError('This mouse isn\'t defined in the settings')
    session = Session(mouse)  # Start a new session for the mouse

    try:
        to_run(session, *mouse_settings[mouse])  # Run the task
        session.smooth_finish = True
        print('smooth finish')
    except KeyboardInterrupt:  # Catch if the task is stopped via ctrl-C or the stop button
        session.halted = True
    finally:
        session.end()


if __name__ == "__main__":
    main('testmouse', cued_forgo)
