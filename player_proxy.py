import json

from subprocess import Popen, PIPE


class PlayerProxy:
    def __init__(self, program_path):
        self.stderr = open(f'./players/{program_path}-log.txt', mode='a')
        self.process = Popen((f'./{program_path}',), cwd='./players', stdin=PIPE, stdout=PIPE, stderr=self.stderr, universal_newlines=True)

    def get_action(self, observation):
        self.process.stdin.write(f'{json.dumps(observation)}\n')

        action = json.loads(self.process.stdout.readline())

        return action['acceleration'], action['braking'], action['steering']

    def done(self):
        self.process.stdin.close()
        self.process.kill()

        self.stderr.close()
