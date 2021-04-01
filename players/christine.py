import json
import random
import sys


class Christine:
    def _reset_action(self):
        if random.uniform(0, 1) < 0.9:
            self.acceleration = random.uniform(-0.5, 1)
            self.braking = 0
        else:
            self.acceleration = 0
            self.braking = random.uniform(0, 1)

        self.steering = random.uniform(-1, 1)

    def __init__(self):
        print('*** Christine ***', file=sys.stderr)  # 自分のプログラムのログであることを確認できるように、プログラム名を出力しておきます。

        self.c = 0

        self._reset_action()

    def get_action(self, observation):
        self.c += 1

        if self.c > 60:
            self._reset_action()
            self.c = 0

        return self.acceleration, self.braking, self.steering


christine = Christine()

while True:
    try:
        observation = json.loads(input())

        acceleration, breaking, steering = christine.get_action(observation)

        print(json.dumps({
            'acceleration': acceleration,
            'braking': breaking,
            'steering': steering
        }))

    except EOFError:
        print('finished!', file=sys.stderr)
        break
