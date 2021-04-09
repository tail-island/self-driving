import cv2
import json
import numpy as np
import sys

from funcy import concat
from math import pi
from operator import itemgetter


def normalize_angle(angle):
    result = (angle + pi * 2) % (pi * 2)

    return result if result < pi else result - pi * 2


def get_nearest_star(observation):
    return min(observation['stars'], key=itemgetter('position_length'))


def find_objects_to_avoid(goal, collection):
    # ゴールよりも手前にあって、ゴールへの角度の左右22.5°の範囲内にあるものを避けるべき対象群とします。
    return filter(lambda object: object['position_length'] < goal['position_length'] and -pi / 8 < normalize_angle(object['position_angle'] - goal['position_angle']) < pi / 8, collection)


def get_objects_to_avoid(observation, goal):
    # 他の車と障害物の中から、避けるべき対象群を取得します。
    return tuple(find_objects_to_avoid(goal, concat(observation['other_cars'], observation['obstacles'])))


def get_object_to_avoid(observation, goal):
    objects_to_avoid = get_objects_to_avoid(observation, goal)

    if not objects_to_avoid:
        return None

    # 避けるべき対象群の中で一番近いものを、避けるべき対象とします。
    return min(objects_to_avoid, key=itemgetter('position_length'))


def get_angle_to_go(observation):
    # 最も近いスターを探します。
    nearest_star = get_nearest_star(observation)

    # 避けるべき対象を取得します。
    object_to_avoid = get_object_to_avoid(observation, nearest_star)

    # 避けるべき対象がないなら……
    if not object_to_avoid:
        # 一番近いスターに直進します。
        return nearest_star['position_angle']

    # 避けるべき対象を（少し大げさに）避ける角度を返します。
    return min(normalize_angle(object_to_avoid['position_angle'] - pi / 4), normalize_angle(object_to_avoid['position_angle'] + pi / 4), key=abs)


# デバッグ用に可視化します
def visualize(observation):
    # 描画関数。
    def plot_body(body, color, thickness=1):
        cv2.circle(image, (320 + int(np.cos(body['position_angle']) * body['position_length']), 320 - int(np.sin(body['position_angle']) * body['position_length'])), 5, color, thickness=thickness)

    # 可視化用の画像を作成します。
    image = np.zeros((641, 641, 3), dtype=np.uint8)

    # x軸とy軸を描画します。
    cv2.line(image, (0, 320), (640, 320), (128, 128, 128))
    cv2.line(image, (320, 0), (320, 640), (128, 128, 128))

    # 他の参加者の自動車を描画します。
    for body in observation['other_cars']:
        plot_body(body, (255, 128, 128))

    # 障害物を描画します。
    for body in observation['obstacles']:
        plot_body(body, (192, 192, 192))

    # スターを表がします。
    for body in observation['stars']:
        plot_body(body, (128, 255, 128))

    # try4のアルゴリズムをなぞります。
    nearest_star = get_nearest_star(observation)
    objects_to_avoid = get_objects_to_avoid(observation, nearest_star)
    object_to_avoid = get_object_to_avoid(observation, nearest_star)

    # 一番近い星を緑で塗りつぶします。
    plot_body(nearest_star, (0, 255, 0), thickness=-1)

    # 一番近い星の左右22.5度の線を描画します。この線の間にあるのが、避けるべき対象群。
    cv2.line(image, (320, 320), (320 + int(np.cos(nearest_star['position_angle'] - np.pi / 8) * nearest_star['position_length']), 320 - int(np.sin(nearest_star['position_angle'] - np.pi / 8) * nearest_star['position_length'])), (128, 128, 192))
    cv2.line(image, (320, 320), (320 + int(np.cos(nearest_star['position_angle'] + np.pi / 8) * nearest_star['position_length']), 320 - int(np.sin(nearest_star['position_angle'] + np.pi / 8) * nearest_star['position_length'])), (128, 128, 192))

    if object_to_avoid:
        # 避けるべき対象群を赤で描画します。
        for body in objects_to_avoid:
            plot_body(body, (0, 0, 255))

        # 避けるべき対象を赤で塗りつぶします。
        plot_body(object_to_avoid, (0, 0, 255), thickness=-1)

        # try4のアルゴリズムをなぞります。
        angle_1 = normalize_angle(object_to_avoid['position_angle'] + np.pi / 4)
        angle_2 = normalize_angle(object_to_avoid['position_angle'] - np.pi / 4)
        angle_to_go = get_angle_to_go(observation)

        # 障害物の左を抜けるコースと、障害物の右を抜けるコースを薄い緑で描画します。
        cv2.line(image, (320, 320), (320 + int(np.cos(angle_1) * 32), 320 - int(np.sin(angle_1) * 32)), (128, 192, 128))
        cv2.line(image, (320, 320), (320 + int(np.cos(angle_2) * 32), 320 - int(np.sin(angle_2) * 32)), (128, 192, 128))

        # 進もうとしているコースを、緑で長めに描画します。
        cv2.line(image, (320, 320), (320 + int(np.cos(angle_to_go) * 64), 320 - int(np.sin(angle_to_go) * 64)), (0, 255, 0))

    cv2.imshow('observation', image)
    cv2.waitKey(1)


class SteerAndAccelBrakeAvoid:
    def __init__(self, visualize=False):
        # 自分のプログラムのログであることを確認できるように、プログラム名を標準エラー出力に出力しておきます。
        print('*** SteerAndAccelBrakeAvoid ***', file=sys.stderr)

        print(visualize, file=sys.stderr)
        self.visualize = visualize

    def get_action(self, observation):
        if self.visualize:
            visualize(observation)

        # 進むべき方向を取得します。
        angle_to_go = get_angle_to_go(observation)

        # 進むべき方向が正面の場合は……
        if -pi / 8 < angle_to_go < pi / 8:
            # アクセル全開で、進むべき方向に向くように弱めにステアリングを切ります。
            return 1.0, 0.0, angle_to_go * 0.5

        # 進むべき方向が正面ではない場合で……
        else:
            # 速度が速い場合は……
            if observation['my_car']['velocity_length'] > 2.5:
                # まずは減速します。
                return 0.0, 1.0, 0.0

            # 速度が遅い場合は……
            else:
                # アクセル弱めで、進むべき角度に向くように強くステアリングを切ります。
                return 0.25, 0.0, angle_to_go * 2


def main(visualize=False):
    player = SteerAndAccelBrakeAvoid(visualize)

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
    from argparse import ArgumentParser

    parser = ArgumentParser()
    parser.add_argument('--visualize', action='store_true')

    args = parser.parse_args()

    main(visualize=args.visualize)
