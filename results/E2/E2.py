import time

import pandas as pd

from DockerClient import DockerInfo
from HttpClient import HttpClient
from agent.DQN import DQN, STATE_DIM
from agent.Global_Service_Optimizer import Global_Service_Optimizer
from agent.ScalingAgent_v2 import ScalingAgent
from slo_config import PW_MAX_CORES

container_1 = DockerInfo("multiscaler-video-processing-a-1", "172.18.0.4", "Alice")
container_2 = DockerInfo("multiscaler-video-processing-b-1", "172.18.0.5", "Bob")
p_s = "http://172.18.0.2:9090"
http_client = HttpClient()

nn = "./networks"
df = pd.read_csv("LGBN.csv")
reps = 5
changes = 10

max_cores = PW_MAX_CORES
pixel_t, fps_t = 1400, 25
starting_pixel, starting_cores = 1100, 2

dqn = DQN(state_dim=STATE_DIM, action_dim=5, force_restart=True, nn_folder=nn)
dqn.train_dqn_from_env(df=df, suffix=f"5")

agent_1 = ScalingAgent(container=container_1, prom_server=p_s, thresholds=(pixel_t, fps_t),
                       dqn=dqn, log=f"S1.1", max_cores=max_cores)
agent_2 = ScalingAgent(container=container_2, prom_server=p_s, thresholds=(pixel_t, fps_t),
                       dqn=dqn, log=f"S1.2", max_cores=max_cores)

glo = Global_Service_Optimizer(agents=[agent_1, agent_2])


def reset_container_params(c, pixel, cores):
    http_client.change_config(c.ip_a, {'pixel': int(pixel)})
    http_client.change_threads(c.ip_a, int(cores))

def start_greedy_agents():
    reset_container_params(container_1, starting_pixel, starting_cores)
    reset_container_params(container_2, starting_pixel, starting_cores)
    time.sleep(2)

    agent_1.start()
    agent_2.start()
    time.sleep(15)

    # agent_1.stop()
    # agent_2.stop()


# TODO: 2) We will let the main class analyze how the SLO-F can be improved
# TODO: 3) This is orchestrated and we measure the improvement
def improve_global_slof():
    for i in range(1, changes + 1):
        glo.estimate_swapping()
        glo.swap_core()

        time.sleep(10)


def visualize_data():
    pass


if __name__ == '__main__':
    start_greedy_agents()
    improve_global_slof()
    visualize_data()