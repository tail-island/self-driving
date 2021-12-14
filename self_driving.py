import os
import shutil

from funcy import first, last, second
from glob import glob
from random import sample
from subprocess import PIPE, run
from datetime import datetime


def main():
    starting_datetime = datetime.now()
    player_names = tuple(sorted(map(lambda bat_file_path: first(last(bat_file_path.split(os.path.sep)).split('.')), glob('.\\players\\*.bat'))))

    while ((now := datetime.now()) - starting_datetime).total_seconds() < 72 * 60 * 60:
        game_name = f'{now.year:04}-{now.month:02}-{now.day:02}-{now.hour:02}-{now.minute:02}-{now.second:02}'

        run_result = run(f'python game.py --animation {" ".join(sample(player_names, 8))}', shell=True, stdout=PIPE, universal_newlines=True)

        shutil.move('game.mp4', f'.\\results\\{game_name}.mp4')

        with open('.\\results\\scores.txt', mode='a') as f:
            print(game_name, file=f)
            for result in run_result.stdout.splitlines()[2:]:
                print(result, file=f)
            print(file=f)

        with open('.\\results\\orders.txt', mode='a') as f:
            last_score = -1
            order = 0

            print(game_name, file=f)
            for i, (player_name, player_score) in enumerate(sorted(map(lambda result: (result.split('\t')[0], int(result.split('\t')[1])), run_result.stdout.splitlines()[2:]), key=second, reverse=True)):
                if player_score != last_score:
                    order = i + 1
                    last_score = player_score

                print(f'{player_name}\t{order}', file=f)
            print(file=f)

        # run('taskkill /im TestDrive.exe /f /t')


if __name__ == '__main__':
    main()
