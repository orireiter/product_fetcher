from RabbitClass import Rabbit
'''
    #Basic Send Example1#
    # (just send)
    sender = Rabbit()

    sender.declare_queue('example1',durable=True)
    print(sender.send_one('example1',"test1"))
    print("done sending\n\n\n")
    sender.close_connection()

'''

'''
    #Basic send example2#
    #(send and wait for an answer)


    send_receive = Rabbit()
    send_receive.declare_queue('example2', durable=True)

    answer = send_receive.send_n_receive('example2', str("check 123"))
    print(answer)
'''