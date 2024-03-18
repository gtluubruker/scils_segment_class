import os
import sys
import argparse
from scilslab import LocalSession


def list_regions():
    parser = argparse.ArgumentParser()
    parser.add_argument('--scils',
                        help='Input .slx file.',
                        required=True,
                        type=str)
    args = vars(parser.parse_args())
    if not os.path.exists(args['scils']):
        print('Input path does not exist...')
        print('Exiting...')
        sys.exit(1)

    with LocalSession(filename=args['scils']) as session:
        data = session.dataset_proxy
        regions = data.get_region_tree().get_all_regions()
        regions = [i.name for i in regions]
        regions = [i.split('/')[-1] if '/' in i else i for i in regions]
        for i in regions:
            print('"' + i + '"')
