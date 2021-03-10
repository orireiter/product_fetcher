from json import loads
import yaml

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
    except KeyError:
        return "ERROR: one of the keys given does NOT exist"
    return conf


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
