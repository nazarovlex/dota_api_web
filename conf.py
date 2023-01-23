import yaml
config = yaml.load(open("conf.yaml"), Loader=yaml.Loader)
api_token = config["api_token"]
master_id = config["master_id"]