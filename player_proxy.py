import json
import os

from funcy import concat, first, repeat, rest
from subprocess import PIPE, Popen
from time import time


class PlayerProxy:
    def __init__(self, program_name):
        self.name = program_name.replace('.bat', '')

        self.time_over = False
        self.time_limits = concat((30 * 2,), repeat(0.5 * 2))

        self.stderr = open(os.path.join('.', 'players', f'{program_name}-log.txt'), mode='a')
        self.process = Popen((os.path.join('.', program_name),), cwd=os.path.join('.', 'players'), shell=True, stdin=PIPE, stdout=PIPE, stderr=self.stderr, universal_newlines=True)

    def get_action(self, observation):
        if self.time_over:
            return 0, 0, 0

        self.process.stdin.write(f'{json.dumps(observation)}\n')
        self.process.stdin.flush()

        starting_time = time()
        action_string = self.process.stdout.readline()
        elapsed_time = time() - starting_time

        if elapsed_time > first(self.time_limits):
            self.time_over = True
            self.stderr.write(f'*** time over. elapsed time: {elapsed_time} sec. ***\n')

        self.time_limits = rest(self.time_limits)

        action = json.loads(action_string)

        return action['acceleration'], action['braking'], action['steering']

    def done(self):
        self.process.stdin.close()

        self.process.kill()

        self.stderr.close()
