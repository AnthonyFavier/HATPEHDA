#!/usr/bin/env python3
import sys

from hatpehda_pkg import gui 
from hatpehda_pkg import hatpehda
from hatpehda_pkg import CommonModule as CM
from hatpehda_pkg import NodeModule as NM

from copy import deepcopy
import time

r_node = None

######################################################
################### Obs functions ###################
######################################################


######################################################
################### Primitive tasks ##################
######################################################

# go behind car #
def GoBehindCarDonecond(agents, state, agent):
    return get_at(state, agent)=="rear"
def GoBehindCarPrecond(agents, state, agent):
    return get_at(state, agent)=="front"
def GoBehindCarEff(agents, state_in, state_out, agent):
    agents.set_fluent_loc("at_"+agent, "rear")
    set_at(state_out, agent, "rear")
GoBehindCarAg = hatpehda.OperatorAg("go_behind_car", donecond=GoBehindCarDonecond, precond=GoBehindCarPrecond, effects=GoBehindCarEff)

# go front car #
def GoFrontCarDonecond(agents, state, agent):
    return get_at(state, agent)=="front"
def GoFrontCarPrecond(agents, state, agent):
    return get_at(state, agent)=="rear"
def GoFrontCarEff(agents, state_in, state_out, agent):
    agents.set_fluent_loc("at_"+agent, "front")
    set_at(state_out, agent, "front")
GoFrontCarAg = hatpehda.OperatorAg("go_front_car", donecond=GoFrontCarDonecond, precond=GoFrontCarPrecond, effects=GoFrontCarEff)

#########
# ROBOT #
#########

# refill washer #
def RefillWasherDonecond(agents, state, agent):
    return state.washer.val=="full"
def RefillWasherPrecond(agents, state, agent):
    return state.washer.val=="low" and state.hood.val=="open"
def RefillWasherEff(agents, state_in, state_out, agent):
    state_out.washer.val = "full"
RefillWasherAg = hatpehda.OperatorAg("refill_washer", donecond=RefillWasherDonecond, precond=RefillWasherPrecond, effects=RefillWasherEff)

# refill oil #
def RefillOilDonecond(agents, state, agent):
    return state.oil.val=="full"
def RefillOilPrecond(agents, state, agent):
    return state.oil.val=="low" and state.hood.val=="open"
def RefillOilEff(agents, state_in, state_out, agent):
    state_out.oil.val = "full"
RefillOilAg = hatpehda.OperatorAg("refill_oil", donecond=RefillOilDonecond, precond=RefillOilPrecond, effects=RefillOilEff)

# store oil #
def StoreOilDonecond(agents, state, agent):
    return state.at_oil_bottle.val=="cabinet"
def StoreOilPrecond(agents, state, agent):
    return state.at_oil_bottle.val=="front"
def StoreOilEff(agents, state_in, state_out, agent):
    agents.set_fluent_loc("at_oil_bottle", "cabinet")
    state_out.at_oil_bottle.val = "cabinet"
StoreOilAg = hatpehda.OperatorAg("store_oil", donecond=StoreOilDonecond, precond=StoreOilPrecond, effects=StoreOilEff)


#########
# HUMAN #
#########

# replace rear light #
def ReplaceRearLightDonecond(agents, state, agent):
    return state.rear_light.val=="new"
def ReplaceRearLightPrecond(agents, state, agent):
    return state.rear_light.val=="old" and get_at(state, agent)=="rear"
def ReplaceRearLightEff(agents, state_in, state_out, agent):
    state_out.rear_light.val="new"
ReplaceRearLightAg = hatpehda.OperatorAg("replace_rear_light", donecond=ReplaceRearLightDonecond, precond=ReplaceRearLightPrecond, effects=ReplaceRearLightEff)

# check right light #
def CheckRightLightDonecond(agents, state, agent):
    return state.right_light.val=="ok"
def CheckRightLightPrecond(agents, state, agent):
    return state.right_light.val=="todo" and get_at(state, agent)=="front"
def CheckRightLightEffects(agents, state_in, state_out, agent):
    state_out.right_light.val="ok"
CheckRightLightAg = hatpehda.OperatorAg("check_right_light", donecond=CheckRightLightDonecond, precond=CheckRightLightPrecond, effects=CheckRightLightEffects)

# check left light #
def CheckLeftLightDonecond(agents, state, agent):
    return state.left_light.val=="ok"
def CheckLeftLightPrecond(agents, state, agent):
    return state.left_light.val=="todo" and get_at(state, agent)=="front"
def CheckLeftLightEffects(agents, state_in, state_out, agent):
    state_out.left_light.val="ok"
CheckLeftLightAg = hatpehda.OperatorAg("check_left_light", donecond=CheckLeftLightDonecond, precond=CheckLeftLightPrecond, effects=CheckLeftLightEffects)

# close hood #
def CloseHoodDonecond(agents, state, agent):
    return state.hood.val=="closed"
def CloseHoodPrecond(agents, state, agent):
    return state.hood.val=="open" and get_at(state, agent)=="front" and state.washer.val=="full" and state.oil.val=="full" and state.left_light.val=="ok" and state.right_light.val=="ok" and state.rear_light.val=="new"
def CloseHoodEff(agents, state_in, state_out, agent):
    state_out.hood.val="closed"
CloseHoodAg = hatpehda.OperatorAg("close_hood", donecond=CloseHoodDonecond, precond=CloseHoodPrecond, effects=CloseHoodEff)

common_ag = [GoFrontCarAg, GoBehindCarAg]
robot_operator_ag = common_ag + [RefillOilAg, RefillWasherAg, StoreOilAg]
human_operator_ag = common_ag +  [ReplaceRearLightAg, CheckLeftLightAg, CheckRightLightAg, CloseHoodAg]


######################################################
################### Abstract Tasks ###################
######################################################

# Car maintenance #
def dec_car_maintenance_R(agents, state, agent):
    return [("go_front_car",), ("refill_washer",), ("refill_oil",), ("store_oil",)]
def dec_car_maintenance_H(agents, state, agent):
    return [("Handling_lights",), ("Closing_hood",)]

# Handling ligths #
def dec_handling_lights_start_replace(agents, state, agent):
    if state.rear_light.val == "new" and (state.right_light == "ok" and state.left_light=="ok"):
        return []
    if state.rear_light.val == "new" and not (state.right_light == "ok" and state.left_light=="ok"):
        return [("Checking_front_lights",)]
    if not state.rear_light.val == "new" and (state.right_light == "ok" and state.left_light=="ok"):
        return [("Replacing_rear_light",)]
    if not state.rear_light.val == "new" and not (state.right_light == "ok" and state.left_light=="ok"):
        return [("Replacing_rear_light",), ("Checking_front_lights",)]
def dec_handling_lights_start_checking(agents, state, agent):
    if not state.rear_light.val == "new" and not (state.right_light == "ok" and state.left_light=="ok"):
        return [("Checking_front_lights",), ("Replacing_rear_light",)]
    return False

# Replacing_rear_light #
def dec_replacing_rear_light(agents, state, agent):
    if state.rear_light.val == "old":
        return [("go_behind_car",), ("replace_rear_light",)]
    return []

# Checking_front_ligths #
def dec_checking_front_ligths(agents, state, agent):
    return [("go_front_car",), ("check_left_light",), ("check_right_light",)]

# Closing_hood #
def dec_closing_hood(agents, state, agent):
    return [("go_front_car",), ("close_hood",)]

common_methods = [
]
ctrl_methods = common_methods + [
            ("Car_maintenance", dec_car_maintenance_R),
]
unctrl_methods = common_methods + [
            ("Car_maintenance", dec_car_maintenance_H),
            ("Handling_lights", dec_handling_lights_start_replace, dec_handling_lights_start_checking),
            ("Replacing_rear_light", dec_replacing_rear_light),
            ("Checking_front_lights", dec_checking_front_ligths),
            ("Closing_hood", dec_closing_hood),
]


######################################################
###################### Triggers ######################
######################################################

common_triggers = []
robot_triggers = common_triggers + []
human_triggers = common_triggers + []


######################################################
################## Helper functions ##################
######################################################

def get_bin_array(n, max):
    array = [int(x) for x in bin(n)[2:]]
    if len(array)<max:
        for i in range(max-len(array)):
            array = [0] + array
    return array

def get_at(state, agent):
    if agent=="robot":
        return state.at_robot.val
    elif agent=="human":
        return state.at_human.val
    else:
        raise Exception("get at {} not in state.at !".format(agent))

def set_at(state, agent, at):
    if agent=="robot":
        state.at_robot.val = at
    elif agent=="human":
        state.at_human.val = at
    else:
        raise Exception("set at {} not in state.at !".format(agent))

######################################################
######################## MAIN ########################
######################################################

def initDomain(n):
    robot_name = "robot"
    human_name = "human"
    CM.set_robot_name(robot_name)
    CM.set_human_name(human_name)
    CM.init_other_agent_name()

    # Initial state
    initial_state = hatpehda.State("init")

    # Generate initial state
    domains = {
        "washer":           ["low", "full"],
        "oil":              ["low", "full"],
        "rear_light":       ["old", "new"],
        "left_light":       ["todo", "ok"],
        "right_light":      ["todo", "ok"],
        "h_washer":         ["low", "full"],
        "h_oil":            ["low", "full"],
        "h_rear_light":     ["old", "new"],
        "starting_agent":   [robot_name, human_name],
    }
    bin_array = get_bin_array(n, max=len(domains))
    values = {}
    for i,f in enumerate(domains):
        values[f] = domains[f][bin_array[i]]

    # Static properties
    initial_state.create_fluent("self_name", "None", hatpehda.ObsType.OBS, "none", False)
    initial_state.create_fluent("other_agent_name", {robot_name:human_name, human_name:robot_name}, hatpehda.ObsType.OBS, "none", False) 

    # Dynamic properties
    initial_state.create_fluent("at_robot",         "front",                    hatpehda.ObsType.OBS,   "front",    True)
    initial_state.create_fluent("at_human",         "front",                    hatpehda.ObsType.OBS,   "front",    True) 
    initial_state.create_fluent("at_oil_bottle",    "front",                    hatpehda.ObsType.INF,   "front",    True)
    initial_state.create_fluent("washer",           values["washer"],           hatpehda.ObsType.OBS,   "front",    True)
    initial_state.create_fluent("oil",              values["oil"],              hatpehda.ObsType.INF,   "front",    True)
    initial_state.create_fluent("hood",             "open",                     hatpehda.ObsType.OBS,   "front",    True)
    initial_state.create_fluent("rear_light",       values["rear_light"],       hatpehda.ObsType.INF,   "rear",     True)
    initial_state.create_fluent("left_light",       values["left_light"],       hatpehda.ObsType.INF,   "front",    True)
    initial_state.create_fluent("right_light",      values["right_light"],      hatpehda.ObsType.INF,   "front",    True)

    # Robot
    hatpehda.declare_operators_ag(robot_name, robot_operator_ag)
    for me in ctrl_methods:
        hatpehda.declare_methods(robot_name, *me)
    hatpehda.declare_triggers(robot_name, *robot_triggers)
    robot_state = deepcopy(initial_state)
    robot_state.self_name.val = robot_name
    robot_state.__name__ = robot_name + "_init"
    hatpehda.set_state(robot_name, robot_state)
    hatpehda.add_tasks(robot_name, [("Car_maintenance",)])

    # Human
    hatpehda.declare_operators_ag(human_name, human_operator_ag)
    for me in unctrl_methods:
        hatpehda.declare_methods(human_name, *me)
    hatpehda.declare_triggers(human_name, *human_triggers)
    human_state = deepcopy(initial_state)
    human_state.__name__ = human_name + "_init"
    human_state.reset_fluent_locs()
    human_state.self_name.val = human_name
    human_state.washer.val = values["h_washer"]
    human_state.oil.val = values["h_oil"]
    human_state.rear_light.val = values["h_rear_light"]
    hatpehda.set_state(human_name, human_state)
    hatpehda.add_tasks(human_name, [("Car_maintenance",)])

    # Starting Agent
    CM.set_starting_agent(values["starting_agent"])

def node_explo(with_contrib, with_graph, with_delay, n):
    robot_name = CM.get_robot_name()
    human_name = CM.get_human_name()

    print("INITIAL STATES")
    hatpehda.show_init()

    CM.set_debug(True)
    # hatpehda.set_compute_gui(True)
    # hatpehda.set_view_gui(True)
    # hatpehda.set_stop_input(True)
    # hatpehda.set_debug_agenda(True)
    # hatpehda.set_stop_input_agenda(True)

    n_plot = 0
    print("Start first exploration")
    first_explo_dur = time.time()
    first_node, Ns, u_flagged_nodes, n_plot = hatpehda.heuristic_exploration(n_plot)
    first_explo_dur = int((time.time() - first_explo_dur)*1000)
    print("\t=> time spent first exploration = {}ms".format(first_explo_dur))
    # hatpehda.gui.show_tree(first_node, "sol", view=True)
    # hatpehda.gui.show_all(hatpehda.get_last_nodes_action(first_node), robot_name, human_name, with_begin="false", with_abstract="true")
    # input()

    # hatpehda.set_debug(True)
    # hatpehda.set_compute_gui(True)
    # hatpehda.set_view_gui(True)
    # hatpehda.set_stop_input(True)
    # hatpehda.set_debug_agenda(True)
    # hatpehda.set_stop_input_agenda(True)

    print("Start refining u nodes")
    refine_u_dur = time.time()
    hatpehda.refine_u_nodes(first_node, u_flagged_nodes, n_plot)
    refine_u_dur = int((time.time() - refine_u_dur)*1000)
    print("\t=> time spent refining = {}ms".format(refine_u_dur))
    print("Total duration = {}ms".format(first_explo_dur+refine_u_dur))

    # Are beliefs aligned ?
    NM.show_belief_alignmen(first_node)

    # Show final plans
    NM.show_plans_str(first_node)

    print("best_traces:")
    NM.compute_node_metrics(first_node)
    print(NM.get_best_traces(first_node))
    print("best_metrics:")
    print(first_node.best_metrics)


    view=False
    if with_graph:
        hatpehda.gui.show_all(NM.get_last_nodes_action(first_node), robot_name, human_name, n, with_contrib, with_delay, with_begin="false", with_abstract="false", view=view)
        # hatpehda.gui.show_tree(first_node, "sol", view=view)

import click
@click.command(help="INIT_STATE_ID (INT) is the initial state config (Default = 0)")
@click.argument('init_state_id', default=0)
@click.option('--without_contrib', is_flag=True, default=False, help="Disable contribution: only HATPEHDA.")
@click.option('--without_graph', is_flag=True, default=False, help="Disable generation of image graph of solution plan.")
@click.option('--without_delay', is_flag=True, default=False, help="Disable usage of Delay.")
def main(init_state_id, without_contrib, without_graph, without_delay):
    with_contrib = not without_contrib
    with_graph = not without_graph
    with_delay = not without_delay
    n = init_state_id

    print("RUN N={} With={}".format(n, with_contrib))
    initDomain(n)
    CM.set_with_contrib(with_contrib)
    CM.set_with_delay(with_delay)

    node_explo(with_contrib, with_graph, with_delay, n)

if __name__ == "__main__":
    main()