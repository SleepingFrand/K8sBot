import argparse

parser = argparse.ArgumentParser()
parser.add_argument('--config', type=str, help='path to config file')
args = parser.parse_args()
KUBER_CONFIG = args.config