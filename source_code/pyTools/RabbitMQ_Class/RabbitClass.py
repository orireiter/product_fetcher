import pika
import uuid


class Rabbit:
    '''
          A class to represent a connection to RabbitMQ server. 
          Allowing easier use of publishing and consuming messages with the same object, giving the object modularity.

          Attributes
          ----------
          rabbit_parameters: pika.ConnectionParameters
                An object containing parameters such as hostname
                of rabbit server or credentials to connect.
                These are defined upon creating an object and are 
                used when sending, receiving messages.
          connection: pika.BlockingConnection object
                Upon creation of this object with the 
                use of the parameters above, 
                a connection to RabbitMQ server is made.
                Allowing to create a channel.
          channel: connection.channel
                Upon execution, the channel can be used to 
                declare/delete queues, publish/consume messages and more.
          channel.qos:
                Decides how theis object will consume messages in temrs of quality.
                IN THIS CASE it is used to tell the consumer to take 1 message at a time.
                As opposed to taking 10 messages messages from the server at once, and 
                still dealing with them one message at a time.
          callback_queue: str
                (Recommended to leave the default)
                The name of an auto-genereated queue, which is also 
                declared to the server upon init, that will be used if 
                the object executes send_n_receive.
                Meaning - The object needs to have a private queue to get an answer from.
          channel.basic_consume:
                Upon execution it will define the properties of the consumption
                of the private queue (for use of send_n_receive).
                When purely consuming without using the callback_queue, 
                this will overridden and defined again with the relevant queue.
          msg_id: str(uuid4)
                When using send_n_receive(), the message send is 
                tagged with this property, as well as this object,
                so when this object awaits an answer (which will be tagged the same)
                it will know when the dedicated answer arrives.
          response: None/str
                (For the use of send_n_receive) This attribute = None 
                until an answer with the right id arrives. 
                And then response = body of that message.

          Methods 
          -------
          declare_queue(queue_name: str, passive=False, durable=False, exclusive=False, auto_delete=False, arguments=None):
                Declares a queue to the server to be used later on.
          declare_exhange(exchange_name: str, exchange_type='direct', passive=False, durable=False, auto_delete=False, internal=False, arguments=None):
                Declares an exchange to the server to be used later on.
          close_connection:
                Closes the connection to the server.
          check_corr_id(channel, method, properties, body):
                Compares the ID given to the message sent, 
                and the one of message answered.
                If they're the same, self.response=answer's body.
          send_one(queue_name: str, message: str, exchange_name=''):
                Send one message to the server (doesn't wait for any response).
          consume_one(queue_name: str, func):
                Consumes one message from given queue, executes one function 
                when the message is consumed uses it.
          consume_many(queue_name: str, func):
                Same as consume one, but loops on consumption. so each time 
                a message is received the function is executed.
          send_n_receive(queue_name: str, message: str, exchange_name=''):
                Sends one message with an ID, and awaits the arrival of a message with same id.
                To receive an answer the consumer of the original must
                use receive_n_send_one/many. 
          receive_n_send_one(queue_name: str, func):
                Consume one message, execute a function with it, and return an answer
                with the same message ID.
          receive_n_send_many(queue_name: str, func):
                Consumes a message, execute a function with it, and return an answer
                with the same message ID. Keeps looping this way.
    '''

    def __init__(self, host='localhost', callback_queue='', credentials=None):
        '''
              Upon initialization, the object will connect to the server,
              open a channel, declare a callback queue, and basic consume.
              After that, each publish or consume will rely on those.

              Parameters
              ----------
              host: str
                    Hostname of the RabbitMQ server.
              callback_queue: str
                    (Recommended to leave the default)
                    The name of an auto-genereated queue, which is also 
                    declared to the server upon init, that will be used if 
                    the object executes send_n_receive.
                    Meaning - The object needs to have a private queue to get an answer from.
              credentials:
                    If you're not using the default user, 
                    you'll have to specify credentials

              Raises
              ------
              pika.exceptions.AMQPConnectionError:
                    If no connection can be made or the creds are wrong,
                    this error will be raised.
                    It will inform the the user.
        '''

        self.host = host
        self.credentials = credentials
        if credentials == None:
            self.rabbit_parameters = pika.ConnectionParameters(self.host)
        else:
            self.rabbit_parameters = pika.ConnectionParameters(
                host=self.host, credentials=self.credentials)

        try:
            self.connection = pika.BlockingConnection(
                parameters=self.rabbit_parameters)
            self.channel = self.connection.channel()
        except pika.exceptions.AMQPConnectionError:
            raise Exception(
                "Couldn't initialize object.\n           RabbitMQ server could not be contacted...")

        self.channel.basic_qos(prefetch_count=1)

        # declaring queue for returning answers
        queue_default_name = self.channel.queue_declare(
            queue=callback_queue, exclusive=True, auto_delete=True)
        self.callback_queue = queue_default_name.method.queue

        # creating basic consume basic consume for returning answers
        # it listens to the return queue, and activates the id check
        self.channel.basic_consume(
            queue=self.callback_queue,
            on_message_callback=self.check_corr_id,
            auto_ack=True)

    def declare_queue(self, queue_name: str, passive=False, durable=False, exclusive=False, auto_delete=False, arguments=None):
        '''
              Declares a queue to server (just an extension to pika's queue declare)

              Parameters
              ----------
              queue_name str
                    Queue name to declare to the RabbitMQ server.
              passive: bool (optional)
                    If this is checked as True, the method will only
                    check if the queue exists already, without declaring it either way.
                    If it doesn't exist, an exception will be raised.
              durable: bool (optional)
                    Survive reboots of the broker 
              exclusive: bool (optional)
                    Only allow access by the current connection 
              auto_delete: bool (optional)
                    Delete after consumer cancels or disconnects 


              Raises
              ------
              If 'passive' is checked as True, the method will only
              check if the queue exists already, without declaring it either way.
              If it doesn't exist, an exception will be raised.
        '''
        self.channel.queue_declare(queue=queue_name,
                                   passive=passive,
                                   durable=durable,
                                   exclusive=exclusive,
                                   auto_delete=auto_delete,
                                   arguments=arguments)

    def declare_exchange(self, exchange_name: str, exchange_type='direct', passive=False, durable=False, auto_delete=False, internal=False, arguments=None):
        '''
              Declares an exchange to server (just an extension to pika's exchange declare)

              Parameters
              ----------
              exchange_name str
                    Exchange name to declare to the RabbitMQ server.
              passive: bool (optional)
                    If this is checked as True, the method will only
                    check if the queue exists already, without declaring it either way.
                    If it doesn't exist, an exception will be raised.
              durable: bool (optional)
                    Survive reboots of the broker 
              exclusive: bool (optional)
                    Only allow access by the current connection 
              auto_delete: bool (optional)
                    Delete after consumer cancels or disconnects 
              internal: bool (optional)
                    Can only be published to by other exchanges
              exchange_type: str (optional)
                    The exchange type to use 

              Raises
              ------
              If 'passive' is checked as True, the method will only
              check if the exchange exists already, without declaring it either way.
              If it doesn't exist, an exception will be raised.
        '''
        self.channel.exchange_declare(exchange=exchange_name,
                                      exchange_type=exchange_type,
                                      passive=passive,
                                      durable=durable,
                                      auto_delete=auto_delete,
                                      internal=internal,
                                      arguments=arguments)

    def close_connection(self):
        '''
              Closes the object's connection to the server.
        '''
        self.connection.close()

    def check_corr_id(self, ch, method, properties, body):
        '''
              Checks if the received message's Id is the same as this object msgID 
              (which is the Id of the message sent).
              If the IDs are the same, the message's body will fill 
              the object's response. 
              It's usually used only by send_n_receive as a callback function.

              Parameters
              ----------
              ch:
                    A connection object.
              method:
                    A method object of received message.
              properties:
                    A properties object of received message.
              body:
                    the message itself ( a string )
        '''

        if self.msg_id == properties.correlation_id:
            self.response = body

    def send_one(self, queue_name: str, message: str, exchange_name='', **kwargs):
        '''
              Confirms the queue exists and then sends the message given to it.
              By using delivery_mode = 2 the message is marked as persistent and
              is less likely to be lost.

              Parameters
              ----------
              queue_name: str
                    Queue name to send the message to.
              exchange_name: str (optional)
                    Exchange name to send the message to.
              message: str
                    The message that will be sent.

              Raises
              ------
              Checks if the queue exists.
              If it doesn't exist, an exception will be returned.
        '''

        # first check if queue exists
        try:
            self.declare_queue(queue_name, True)

        except:
            return(f'ERROR: Queue named {queue_name} not found. \n       Consider declaring it first.')

        self.channel.basic_publish(exchange=exchange_name,
                                   routing_key=queue_name,
                                   body=str(message),
                                   properties=pika.BasicProperties(delivery_mode=2,))

        return(f'SUCCESS: Message sent to queue named => {queue_name}')

    def send_n_receive(self, queue_name: str, message: str, exchange_name=''):
        '''
              Sends a message and awaits an answer.
              Consumer MUST be either receive_n_send_one/many.
              steps:
              ------
                    1)Confirms the queue exists and then sends the message given to it.
                    2)Cleans the response attribute (to be used by the answer later).
                    3)Generates an ID and sets it to this objects msg_id.
                    4)Creates a pika properties objects, that sets the message_id and call back queue.
                    now when the message will be sent it will have the id as this object, and will be 
                    returned to the callback queue( which this object listens to for 
                    answers by this function).
                    5)Publishes the message along the properties sent.
                    6)Starts listening to to the callback queue and awaits an answer with the original ID.
                    7)Returns the answer
              notes:
                    By using delivery_mode = 2 the message is marked as persistent and
                    is less likely to be lost.

              Parameters
              ----------
              queue_name: str
                    Queue name to send the message to.
              exchange_name: str (optional)
                    Exchange name to send the message to.
              message: str
                    The message that will be sent.

              Raises
              ------
              Checks if the queue exists.
              If it doesn't exist, an exception will be returned.
        '''

        # first check if queue exists
        try:
            self.declare_queue(queue_name, True)
        except:
            self.__init__(host=self.host, credentials=self.credentials)
            # return(f"ERROR: Queue named {queue_name} not found. \n       Consider declaring it first.")

        self.response = None
        self.msg_id = str(uuid.uuid4())
        publish_params = pika.BasicProperties(
            correlation_id=self.msg_id, reply_to=self.callback_queue,)

        self.channel.basic_publish(exchange=exchange_name,
                                   routing_key=queue_name,
                                   properties=publish_params,
                                   body=str(message))

        while self.response == None:
            self.connection.process_data_events()
        return self.response.decode('utf-8')

    def receive_n_send_one(self, queue_name: str, func):
        '''
              Receives a message, executes a function with it and 
              returns an answer.
              It then stops consuming.\n
              TO AVOID ERRORS, make sure the callback function 
              returns a correct string.\n
              ie if it's a dictionary - use json.dumps() and not str() and so on.


              Parameters
              ----------
              queue_name: str
                    Queue name to send the message to.
              func: function
                    The function that will be use the message.

              Raises
              ------
              Checks if the queue exists.
              If it doesn't exist, an exception will be returned.
              Tries to execute the function.
              If it can't, an exception will be returned.
        '''

        # first check if queue exists
        try:
            self.declare_queue(queue_name, True)
        except:
            return(f'ERROR: Queue named {queue_name} not found. \n       Consider declaring it first.')

        def callback(ch, method, properties, body):
            try:
                result = func(body.decode('utf-8'))
            except:
                print(
                    f"ERROR: Couldn't execute the function named {func.__name__} on the given message")
                return f"ERROR: Couldn't execute the function named {func.__name__} on the given message"

            ch.basic_publish(exchange='',
                             routing_key=properties.reply_to,
                             properties=pika.BasicProperties(
                                 correlation_id=properties.correlation_id),
                             body=str(result))
            ch.basic_ack(delivery_tag=method.delivery_tag)
            ch.stop_consuming()
            return result
        self.channel.basic_consume(
            queue=queue_name, on_message_callback=callback)
        self.channel.start_consuming()

    def receive_n_send_many(self, queue_name: str, func, reply_to_exchange: str=''):
        '''
              Receives a message, executes a function with it and returns an answer.
              Can consume endless messages.
              Check send_n_receive for more info.\n
              TO AVOID ERRORS, make sure the callback function 
              returns a correct string.\n
              ie if it's a dictionary - use json.dumps() and not str() and so on.

              Parameters
              ----------
              queue_name: str
                    Queue name to receive messages from.
              func: function
                    The function that will use the message.

              Raises
              ------
              Checks if the queue exists.
              If it doesn't exist, an exception will be returned.
              Tries to execute the function.
              If it can't, an exception will be returned.
        '''

        # first check if queue exists
        try:
            self.declare_queue(queue_name, True)
        except:
            return(f'ERROR: Queue named {queue_name} not found. \n       Consider declaring it first.')

        def callback(ch, method, properties, body):
            try:
                result = func(body.decode('utf-8'))
            except:
                print(
                    f"ERROR: Couldn't execute the function named {func.__name__} on the given message")
                return f"ERROR: Couldn't execute the function named {func.__name__} on the given message"

            ch.basic_publish(exchange=reply_to_exchange,
                             routing_key=properties.reply_to,
                             properties=pika.BasicProperties(
                                 correlation_id=properties.correlation_id),
                             body=str(result))
            ch.basic_ack(delivery_tag=method.delivery_tag)
            return result
        self.channel.basic_consume(
            queue=queue_name, on_message_callback=callback)
        self.channel.start_consuming()

    def consume_one(self, queue_name: str, func):
        '''
              Receives a message, executes a function with it.
              It then stops consuming.

              Parameters
              ----------
              queue_name: str
                    Queue name to send the message to.
              func: function
                    The function that will be use the message.

              Raises
              ------
              Checks if the queue exists.
              If it doesn't exist, an exception will be returned.
              Tries to execute the function.
              If it can't, an exception will be returned.
        '''

        # first check if queue exists
        try:
            self.declare_queue(queue_name, True)
        except:
            return(f'ERROR: Queue named {queue_name} not found. \n       Consider declaring it first.')

        def callback(ch, method, properties, body):
            try:
                result = func(body.decode('utf-8'))
                ch.basic_ack(delivery_tag=method.delivery_tag)
            except:
                print(
                    f"ERROR: Couldn't execute the function named {func.__name__} on the given message")
                return f"ERROR: Couldn't execute the function named {func.__name__} on the given message"
            ch.stop_consuming()
            return result
        self.channel.basic_consume(
            queue=queue_name, on_message_callback=callback)
        self.channel.start_consuming()

    def consume_many(self, queue_name: str, func):
        '''
              Receives a message, executes a function with it.
              It can consume endlessly.

              Parameters
              ----------
              queue_name: str
                    Queue name to send the message to.
              func: function
                    The function that will be use the message.

              Raises
              ------
              Checks if the queue exists.
              If it doesn't exist, an exception will be returned.
              Tries to execute the function.
              If it can't, an exception will be returned.
        '''
        # first check if queue exists
        try:
            self.declare_queue(queue_name, True)
        except:
            return(f'ERROR: Queue named {queue_name} not found. \n       Consider declaring it first.')

        def callback(ch, method, properties, body):
            try:
                result = func(body.decode('utf-8'))
                ch.basic_ack(delivery_tag=method.delivery_tag)
            except:
                print(
                    f"ERROR: Couldn't execute the function named {func.__name__} on the given message")
                return f"ERROR: Couldn't execute the function named {func.__name__} on the given message"
            return result

        self.channel.basic_consume(
            queue=queue_name, on_message_callback=callback)
        self.channel.start_consuming()

    def receive_n_redirect_many(self, queue_name: str, func, reply_to_exchange: str=''):
        '''
              Receives a message, executes a function with it and returns an answer.
              it can optionally redirect the message elsewhere and not return it.
              This will happen when the function that was callbacked will return
              a dictionary containing a key 'redirect_to' with the value 
              of the queue to be redirected to, and a key 'exchange' with
              the value of the exchange of said queue.
              Can consume endless messages.
              Check send_n_receive for more info.\n
              TO AVOID ERRORS, make sure the callback function 
              returns a correct string.\n
              ie if it's a dictionary - use json.dumps() and not str() and so on.

              Parameters
              ----------
              queue_name: str
                    Queue name to receive messages from.
              func: function
                    The function that will use the message.

              Raises
              ------
              Checks if the queue exists.
              If it doesn't exist, an exception will be returned.
              Tries to execute the function.
              If it can't, an exception will be returned.
        '''

        # first check if queue exists
        try:
            self.declare_queue(queue_name, True)
        except:
            return(f'ERROR: Queue named {queue_name} not found. \n       Consider declaring it first.')

        def callback(ch, method, properties, body):
            try:
                result = func(body.decode('utf-8'))
            except:
                print(
                    f"ERROR: Couldn't execute the function named {func.__name__} on the given message")
                return f"ERROR: Couldn't execute the function named {func.__name__} on the given message"

            if type(result) == type({}) and 'redirect_to' in result and 'exchange' in result:
                ch.basic_publish(exchange=result['exchange'],
                                 routing_key=result['redirect_to'],
                                 properties=pika.BasicProperties(
                                     correlation_id=properties.correlation_id,
                                     reply_to=properties.reply_to),
                                 body=body.decode('utf-8'))
            else:
                ch.basic_publish(exchange=reply_to_exchange,
                                 routing_key=properties.reply_to,
                                 properties=pika.BasicProperties(
                                     correlation_id=properties.correlation_id),
                                 body=str(result))
            ch.basic_ack(delivery_tag=method.delivery_tag)
            return result
        self.channel.basic_consume(
            queue=queue_name, on_message_callback=callback)
        self.channel.start_consuming()
