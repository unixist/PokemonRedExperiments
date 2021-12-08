from os.path import exists
import uuid
from red_gym_env import RedGymEnv
import gym
from stable_baselines3 import A2C, PPO
from stable_baselines3.common import env_checker
from stable_baselines3.common.vec_env import DummyVecEnv, SubprocVecEnv
from stable_baselines3.common.utils import set_random_seed



def make_env(rank, env_conf, seed=0):
    """
    Utility function for multiprocessed env.

    :param env_id: (str) the environment ID
    :param num_env: (int) the number of environments you wish to have in subprocesses
    :param seed: (int) the inital seed for RNG
    :param rank: (int) index of the subprocess
    """
    def _init():
        env = RedGymEnv(env_conf)
        env.seed(seed + rank)
        return env
    set_random_seed(seed)
    return _init


if __name__ == '__main__':

    ep_length = 2048 * 3
    sess_name = str(uuid.uuid4())[:8]

    env_config = {
                'headless': True, 'save_final_state': True, 'early_stop': False,
                'action_freq': 24, 'init_state': '../init.state', 'max_steps': ep_length, 
                'print_rewards': True,'save_video': True, 'session_name': sess_name,
                'gb_path': '../PokemonRed.gb', 'debug': False, 'sim_frame_dist': 7_000_000.0
            }
    
    num_cpu = 30  # Also sets the number of episodes per training iteration
    env = SubprocVecEnv([make_env(i, env_config) for i in range(num_cpu)])
    #env_checker.check_env(env)
    learn_steps = 40
    file_name = 'poke_'
    if exists(file_name + '.zip'):
        print('loading checkpoint')
        model = PPO.load(file_name, env=env)
    else:
        model = PPO('CnnPolicy', env, verbose=1, n_steps=ep_length, batch_size=128, n_epochs=3, gamma=0.995)

    for i in range(learn_steps):
        model.learn(total_timesteps=2048*3*128)
        model.save(file_name+str(i))
