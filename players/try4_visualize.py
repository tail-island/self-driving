import cv2
import numpy as np

from try4 import get_angle_to_go, get_nearest_star, get_object_to_avoid, get_objects_to_avoid, normalize_angle


def visualize(observation):
    def plot_body(body, color, thickness=1):
        cv2.circle(image, (320 + int(np.cos(body['position_angle']) * body['position_length']), 320 - int(np.sin(body['position_angle']) * body['position_length'])), 5, color, thickness=thickness)

    image = np.zeros((641, 641, 3), dtype=np.uint8)

    cv2.line(image, (0, 320), (640, 320), (128, 128, 128))
    cv2.line(image, (320, 0), (320, 640), (128, 128, 128))

    for body in observation['other_cars']:
        plot_body(body, (255, 192, 192))

    for body in observation['obstacles']:
        plot_body(body, (192, 192, 192))

    for body in observation['stars']:
        plot_body(body, (192, 255, 192))

    nearest_star = get_nearest_star(observation)
    objects_to_avoid = get_objects_to_avoid(observation, nearest_star)

    plot_body(nearest_star, (0, 255, 0), thickness=-1)

    cv2.line(image, (320, 320), (320 + int(np.cos(nearest_star['position_angle'] - np.pi / 8) * nearest_star['position_length']), 320 - int(np.sin(nearest_star['position_angle'] - np.pi / 8) * nearest_star['position_length'])), (128, 128, 192))
    cv2.line(image, (320, 320), (320 + int(np.cos(nearest_star['position_angle'] + np.pi / 8) * nearest_star['position_length']), 320 - int(np.sin(nearest_star['position_angle'] + np.pi / 8) * nearest_star['position_length'])), (128, 128, 192))

    for body in objects_to_avoid:
        plot_body(body, (0, 0, 255))

    if objects_to_avoid:
        object_to_avoid = get_object_to_avoid(objects_to_avoid)
        angle_1 = normalize_angle(object_to_avoid['position_angle'] - np.pi / 4)
        angle_2 = normalize_angle(object_to_avoid['position_angle'] + np.pi / 4)
        angle_to_go = get_angle_to_go(observation)

        plot_body(object_to_avoid, (0, 0, 255), thickness=-1)

        cv2.line(image, (320, 320), (320 + int(np.cos(angle_1) * 32), 320 - int(np.sin(angle_1) * 32)), (128, 192, 128))
        cv2.line(image, (320, 320), (320 + int(np.cos(angle_2) * 32), 320 - int(np.sin(angle_2) * 32)), (128, 192, 128))
        cv2.line(image, (320, 320), (320 + int(np.cos(angle_to_go) * 64), 320 - int(np.sin(angle_to_go) * 64)), (0, 255, 0))

    cv2.imshow('observation', image)
    cv2.waitKey(1)


if __name__ == '__main__':
    observation = eval("{'my_car': {'position': [-295.0788439813521, 77.43741000567016], 'angle': 3.0724526371071814, 'velocity_angle': -0.036343847512077865, 'velocity_length': 6.003379173004461, 'steering_angle': -0.08518756822159457, 'steering_torque': -0.0223857373241354, 'score': 0, 'crash_energy': 0.0}, 'other_cars': [{'position_angle': 2.7270008186300814, 'position_length': 446.6423123197093, 'angle': 0.3135327384617721, 'velocity_angle': 3.005979119102131, 'velocity_length': 6.131359608691652, 'steering_angle': 0.5635781465014604, 'score': 0, 'crash_energy': 49.45976303712565}, {'position_angle': -3.003466058165822, 'position_length': 356.54370042736844, 'angle': -1.3962982298439304, 'velocity_angle': -3.0524043852156924, 'velocity_length': 5.702454627525545, 'steering_angle': 0.5262542846601557, 'score': 0, 'crash_energy': 0.0}, {'position_angle': -2.934580849378102, 'position_length': 269.5020499987118, 'angle': -0.6355573573922957, 'velocity_angle': -3.124476825595292, 'velocity_length': 5.26100422234585, 'steering_angle': 0.5236969107177831, 'score': 0, 'crash_energy': 0.0}, {'position_angle': 0.8113543617627546, 'position_length': 113.8878269666947, 'angle': 0.5600036561694175, 'velocity_angle': 2.0020723547518138, 'velocity_length': 2.646326672528007, 'steering_angle': 0.524725334664085, 'score': 0, 'crash_energy': 0.0}, {'position_angle': 2.5759083799065436, 'position_length': 235.31163920666944, 'angle': -0.11378385173592775, 'velocity_angle': 3.1152865865267376, 'velocity_length': 5.324481108848161, 'steering_angle': -0.4129726179020583, 'score': 0, 'crash_energy': 0.05289038502171475}, {'position_angle': 2.6549679801762593, 'position_length': 425.83219471678314, 'angle': 2.5336964761485063, 'velocity_angle': 2.9746652528975783, 'velocity_length': 6.393783390578455, 'steering_angle': -0.07188329631420132, 'score': 0, 'crash_energy': 49.12718503947578}, {'position_angle': 2.8416557631787, 'position_length': 456.3450492008941, 'angle': 2.5450193970680566, 'velocity_angle': 2.9340446352425005, 'velocity_length': 7.410680284025253, 'steering_angle': -0.4713807086530064, 'score': 0, 'crash_energy': 0.0}], 'obstacles': [{'position_angle': 2.445126839092042, 'position_length': 256.00526274483127}, {'position_angle': -2.202191402311003, 'position_length': 832.7775981616268}, {'position_angle': -1.7600055048946812, 'position_length': 284.8347288398028}, {'position_angle': 2.8192291159974907, 'position_length': 863.5481556341925}, {'position_angle': 2.543942305626146, 'position_length': 379.42108212837906}, {'position_angle': 0.8436009417635653, 'position_length': 481.3862091622859}, {'position_angle': -0.4556402660859078, 'position_length': 106.88975977293676}, {'position_angle': 1.7078411255759294, 'position_length': 390.84684040421854}, {'position_angle': 3.0379889600125516, 'position_length': 434.03341286189504}, {'position_angle': -2.376767138741577, 'position_length': 213.64163403466262}, {'position_angle': 2.6270712062731043, 'position_length': 78.78098511756083}, {'position_angle': 1.393001573895651, 'position_length': 717.6532741669674}, {'position_angle': -2.3275761187140223, 'position_length': 1076.9590482468766}, {'position_angle': -3.0889846545958592, 'position_length': 500.4014510359166}, {'position_angle': -2.250548832909729, 'position_length': 59.04589081624068}, {'position_angle': 2.203434283814671, 'position_length': 387.10273785960044}, {'position_angle': 3.0830126660176447, 'position_length': 158.67489434616942}, {'position_angle': -2.1583696811686, 'position_length': 380.80344012373166}, {'position_angle': 1.0836780105501633, 'position_length': 539.4836562052623}, {'position_angle': -2.7516520469736316, 'position_length': 491.09641905858075}, {'position_angle': -2.5754689003268707, 'position_length': 266.055537088534}, {'position_angle': -2.8927108967682402, 'position_length': 404.9822055574565}, {'position_angle': -2.597633820474096, 'position_length': 319.9785892447142}, {'position_angle': -2.4343396174443748, 'position_length': 671.3792736560805}, {'position_angle': -0.4892151541235288, 'position_length': 279.9582667937974}, {'position_angle': -2.823988520620052, 'position_length': 695.8292180070773}, {'position_angle': -0.7230814616829111, 'position_length': 178.82605149448725}, {'position_angle': 2.504041179573216, 'position_length': 518.5499941170607}, {'position_angle': -2.7388901276118034, 'position_length': 1051.9626479149995}, {'position_angle': -2.0866094660981602, 'position_length': 870.4122250453029}, {'position_angle': 1.763911768359078, 'position_length': 226.6648006809148}, {'position_angle': 2.192349180039292, 'position_length': 730.1196634424718}, {'position_angle': -2.194099640636992, 'position_length': 613.305104896544}, {'position_angle': 2.609475478499112, 'position_length': 531.7514767426488}, {'position_angle': 1.167438279583049, 'position_length': 626.4299128408138}, {'position_angle': 2.6339421375283045, 'position_length': 204.83533720556642}, {'position_angle': 3.0718308521314928, 'position_length': 550.7549104050171}, {'position_angle': 1.8541449284475284, 'position_length': 785.772882002275}, {'position_angle': 0.8837036197355292, 'position_length': 763.4496967577243}, {'position_angle': 3.056390398121323, 'position_length': 880.9143472144328}], 'stars': [{'position_angle': 1.1697787788209384, 'position_length': 128.7496999825702}, {'position_angle': 2.478323000946677, 'position_length': 635.6980786622795}]}")

    visualize(observation)
    cv2.waitKey(0)
