import json
import sys

from math import pi
from operator import itemgetter


class SteerAndAccelBrake:
    def __init__(self):
        # 自分のプログラムのログであることを確認できるように、プログラム名を標準エラー出力に出力しておきます。
        print('*** SteerAndAccelBrake ***', file=sys.stderr)

    def get_action(self, observation):
        # 最も近いスターを探します。
        nearest_star = min(observation['stars'], key=itemgetter('position_length'))

        # スターが正面にある場合は……
        if -pi / 8 < nearest_star['position_angle'] < pi / 8:
            # アクセル全開で、スターに向くように弱めにステアリングを切ります。
            return 1.0, 0.0, nearest_star['position_angle'] * 0.5

        # スターが正面にない場合で……
        else:
            # 速度が速い場合は……
            if observation['my_car']['velocity_length'] > 2.5:
                # まずは減速します。
                return 0.0, 1.0, 0.0

            # 速度が遅い場合は……
            else:
                # アクセル弱めで、スターに向くように強くステアリングを切ります。
                return 0.25, 0.0, nearest_star['position_angle'] * 2


def main():
    player = SteerAndAccelBrake()

    print('started!', file=sys.stderr)

    while True:
        try:
            observation = json.loads(input())

            acceleration, breaking, steering = player.get_action(observation)

            print(json.dumps({
                'acceleration': acceleration,
                'braking': breaking,
                'steering': steering
            }))

        except EOFError:
            break

    print('finished!', file=sys.stderr)


if __name__ == '__main__':
    main()
