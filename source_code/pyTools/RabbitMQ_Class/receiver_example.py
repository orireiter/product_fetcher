from RabbitClass import Rabbit
'''
    #Basic receive example1#
    #(consume)
    def message_alterer(msg):
        print(f'the message received is => {msg}')
        print("it will be altered")
        print(f"altered {msg} altered")
        return f"altered {msg} altered"

    receiver = Rabbit()
    receiver.consume_many('example1', message_alterer)
    print('done receiving')
    receiver.close_connection()
'''

'''

    #Basic receive example2#
    #(consume and then answer)
    
    receive_send = Rabbit()

    def message_alterer(msg):
        print(str(msg))
        msg = str(msg) + " test " + str(msg)
        reversed(msg)
        return msg
    receive_send.declare_queue('example2',durable=True)

    receive_send.receive_n_send_many('example2', message_alterer)
'''