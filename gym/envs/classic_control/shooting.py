"""
Classic cart-pole system implemented by Rich Sutton et al.
Copied from http://incompleteideas.net/sutton/book/code/pole.c
permalink: https://perma.cc/C9ZM-652R
"""

import logging
import math
import gym
from gym import spaces
from gym.utils import seeding
import numpy as np
import socket

logger = logging.getLogger(__name__)

class CartPoleEnv(gym.Env):
    metadata = {
        'render.modes': ['human', 'rgb_array'],
        'video.frames_per_second' : 50
    }

    screen_height = 84
    screen_width = 84

    def __init__(self, frameskip=(2,5)):
        #self.tau = 0.02  # seconds between state updates

        #アクション数設定
        self.action_space = spaces.Discrete(17)
        #観測範囲設定
        self.observation_space = spaces.Box(low=0, high=255, shape=(screen_height, screen_width, 3))

        self.frameskip = frameskip
        self._seed()
        self.state = None

        self.steps_beyond_done = None
        self.data = None

        #ソケット作成
        self.s = socket.socket()
        self.port = 11451
        self.s.bind(('', port))
        self.s.listen(5)
        self.c, self.addr = self.s.accept()

    def _seed(self, seed=None):
        self.np_random, seed = seeding.np_random(seed)
        return [seed]

    def _step(self, action):
        reward = 0.0
        assert self.action_space.contains(action), "%r (%s) invalid"%(action, type(action))
        state = self.state

        if isinstance(self.frameskip, int):
            num_steps = self.frameskip
        else:
            num_steps = self.np_random.randint(self.frameskip[0], self.frameskip[1])
        for _ in range(num_steps):
            #num_stepsだけ同じ行動を繰り返す
            self.c.send("2")
            #action送信
            self.c.send(action)

        #生存チェック 生きてたら1 死んでたら-1
        #そのまま報酬
        done = int(self._get_done())
        reward = done
        ob = self._get_obs()

        return ob, reward, done

    def _get_obs(self):
        #画像取ってくる
        self.c.send("1")
        self.data = self.c.recv(1024).strip()
        self.c.send("1")
        buf=''
        recvlen=0
        while recvlen<int(self.data):
                receivedstr=self.request.recv(1024*1024)
                recvlen+=len(receivedstr)
                buf +=receivedstr
        image=np.fromstring(buf,dtype='uint8')

        return image

    def _reset(self):
        self.steps_beyond_done = None

        #初期化処理
        self.c.send("4")
        while true :
            if self.c.recv(1024).strip() == "1":
                break
        return self._get_obs()

    def get_action_meanings(self):
        return [ACTION_MEANING[i] for i in self._action_set]

    def _get_done(self):
        self.c.send("3")
        return self.c.recv(1024).strip()



    ACTION_MEANING = {
        0 : "NOOP",
        1 : "UP",
        2 : "RIGHT",
        3 : "LEFT",
        4 : "DOWN",
        5 : "UPRIGHT",
        6 : "UPLEFT",
        7 : "DOWNRIGHT",
        8 : "DOWNLEFT",
        9 : "SHIFTUP",
        10 : "SHIFTRIGHT",
        11 : "SHIFTLEFT",
        12 : "SHIFTDOWN",
        13 : "SHIFTUPRIGHT",
        14 : "SHIFTUPLEFT",
        15 : "SHIFTDOWNRIGHT",
        16 : "SHIFTDOWNLEFT",
    }
