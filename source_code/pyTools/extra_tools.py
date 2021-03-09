from json import loads
import yaml

# extra tools that can be useful in any project #


'''
    a function that parses a yml and returns a value
    corresponding to the key/keychain supplied
    example for execution: 

 admin_cred = get_Conf(['DBs','products','db_cred'])
 will return admin mysql cred to access the db named products
 in a .yml that looks like this
 DBs:
    products:
        db_cred:
        host: localhost
        user: ori
        password: 123456
        tables:
        - music
        - movies
'''


def get_conf(*key_list):
    conf = yaml.safe_load(open('./config.yml'))
    try:
        for key in list(key_list):
            conf = conf[key]
    except KeyError:
        return "ERROR: one of the keys given does NOT exist"
    return conf


def fix_json_quotings(string):
    fixed_string = string.replace("'", '"')
    fixed_json = loads(fixed_string)
    return(fixed_json)


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
