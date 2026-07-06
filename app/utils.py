import configparser

def get_config_value(section, key):
    config = configparser.ConfigParser()
    config.read('../setup/config.ini')
    return config.get(section, key)

print(get_config_value('PATH', 'invoice_absolute_save_path'))