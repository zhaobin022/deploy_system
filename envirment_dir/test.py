import yaml

with open("openapi_config.yml") as f:
    print yaml.load(f)