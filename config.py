import argparse

parser = argparse.ArgumentParser()
parser.add_argument('--config', type=str, help='path to config file')
parser.add_argument('--telegram', type=str, help='API telegram token')
args = parser.parse_args()
KUBER_CONFIG = args.config
TELEGRAN_TOKEN = args.telegram
