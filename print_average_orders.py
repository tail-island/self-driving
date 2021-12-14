from funcy import second


def get_orders():
    result = {}

    with open('.\\results\\orders.txt') as f:
        for line in f.readlines():
            if len(line.split('\t')) != 2:
                continue

            name = line.split('\t')[0]
            order = int(line.split('\t')[1])

            if name not in result:
                result[name] = [order]
            else:
                result[name].append(order)

    return result


def get_averate_orders():
    result = {}

    for name, orders in get_orders().items():
        result[name] = (sum(orders) / len(orders), len(orders))

    return result


for name, average_order in sorted(get_averate_orders().items(), key=second):
    print(f'{name}\t{average_order[0]:.3f}\t{average_order[1]}')
