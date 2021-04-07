import json
import sys

from math import pi
from operator import itemgetter


class SteerAndAccel:
    def __init__(self):
        # 自分のプログラムのログであることを確認できるように、プログラム名を標準エラー出力に出力しておきます。
        print('*** SteerAndAccel ***', file=sys.stderr)

    def get_action(self, observation):
        # 最も近いスターを探します。
        nearest_star = min(observation['stars'], key=itemgetter('position_length'))

        # スターが正面にある場合はアクセル全開、そうでない場合はアクセルを1/4開けます。
        acceleration = 1.0 if -pi / 8 < nearest_star['position_angle'] < pi / 8 else 0.25

        # ブレーキはつかいません！
        braking = 0

        # 最も近いスターの角度に合わせて、ステアリングを切ります。アクセルを弱めたので、steerの2倍の強さでハンドルを切ってみました。
        steering = nearest_star['position_angle'] * 2

        # アクションを返します。
        return acceleration, braking, steering


def main():
    player = SteerAndAccel()

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
