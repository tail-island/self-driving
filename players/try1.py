import json
import sys

from operator import itemgetter


class Steer:
    def __init__(self):
        # 自分のプログラムのログであることを確認できるように、プログラム名を出力しておきます。
        print('*** Steer ***', file=sys.stderr)

    def get_action(self, observation):
        # 最も近いスターを探します。
        nearest_star = min(observation['stars'], key=itemgetter('position_length'))

        # アクセルは全開
        acceleration = 1

        # ブレーキはつかいません！
        braking = 0

        # スターの角度に合わせて、ステアリングを切ります。
        steering = nearest_star['position_angle']

        return acceleration, braking, steering


def main():
    player = Steer()

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
