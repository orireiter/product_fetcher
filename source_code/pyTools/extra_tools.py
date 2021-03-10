from json import loads
from time import sleep
import yaml
import socket
from .RabbitMQ_Class.RabbitClass import Rabbit

# extra tools that can be useful in any project #


def get_conf(*key_list):
    '''
        a function that parses a yml and returns a value
        corresponding to the key/keychain supplied
        example for execution: 

        admin_cred = get_Conf('DBs','products','db_cred')\n
        will return admin mysql cred to access the db named products\n
        in a .yml that looks like this\n
        DBs:\n
            products:\n
                db_cred:\n
                    host: localhost\n
                    user: ori\n
                    password: 123456\n
                tables:\n
                - music\n
                - movies\n
    '''

    conf = yaml.safe_load(open('./config.yml'))
    try:
        for key in list(key_list):
            conf = conf[key]
        return conf
    except KeyError:
        raise Exception("ERROR: one of the keys given does NOT exist")


def dictionary_repacker(dictionary: dict,
                        originialKey_n_wantedKey_list: list):
    '''
        This function takes a dictionary and repacks it with new keys.
        The second argument is list containing original 
        key paired with a new key (or without it to keep the same name).
        It will return a new dictionary discarded of not given keys.
        \n
        before_dictionary = {"name": "ori", "age": 21, "address": "tlv"}\n
        renew_keys = [['name', 'full_name'], ['age']]\n
        print(dictionary_repacker(before_dictionary, renew_keys))\n
        -> {'full_name': 'ori', 'age': 21}
    '''
    return {key[-1]: dictionary[key[0]]
            for key in originialKey_n_wantedKey_list}


def check_if_port_is_open(hostname: str, port: int):

    socket_object = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    remote_host = (hostname, port)

    # trying to connect to remote port and then closing
    is_open = socket_object.connect_ex(remote_host)
    socket_object.close()

    if is_open == 0:
        return True
    else:
        return False


def wait_for_dependencies(*host_n_port_pairs):
    '''
        Given pairs of hosts and ports, this function 
        keeps waiting for them to open.
        This used to ensure a service will wait for the 
        services it depends on to come online first,
        and prevent it form crashing.\n
        --------
        example:\n
        wait_for_dependencies(["localhost", 27017], ["rabbit.srv", 15672])
    '''
    for host_n_port in host_n_port_pairs:
        is_up = False
        while is_up == False:
            available = check_if_port_is_open(*host_n_port)
            if available:
                print(f"Connected to {host_n_port}!")
                is_up = True
                sleep(2)
            else:
                print(f"Waiting for {host_n_port}")
                sleep(2)
    print("Will initialize service in 5 seconds.")
    sleep(5)


def is_configuration_n_rabbit_up():
    # Upon execution, first wait until it can find the config,
    # and can connect to the rabbit server.
    is_rabbit_up, is_conf_up = False, False
    print("awaiting config")
    while is_conf_up is False:
        try:
            rabbit_host = get_conf('rabbitmq', 'host')
            is_conf_up = True
        except:
            sleep(1)
    print("awaiting connection to RabbitMQ")
    while is_rabbit_up is False:
        try:
            print("attempt")
            rab = Rabbit(host=rabbit_host)
            is_rabbit_up = True
            rab.close_connection()
        except:
            sleep(2)
