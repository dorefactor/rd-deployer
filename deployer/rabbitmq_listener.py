#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import pika
import deployer
import os

# -----------------------------
# DeployQueueListener
# -----------------------------


class DeployQueueListener:

    def __init__(self):
        self.__queue = 'com.dorefactor.deploy.command'
        self.__command = deployer.Command(os.environ.get('RD_API_URL'))

        connection = pika.BlockingConnection(
            pika.ConnectionParameters(host='rabbitmq-host',
                                      credentials=pika.PlainCredentials(os.environ.get('RABBITMQ_USER'),
                                                                        os.environ.get('RABBITMQ_PASSWORD'))))
        self.__channel = connection.channel()
        self.__channel.queue_declare(queue=self.__queue, durable=True)

    def start_consuming(self):
        self.__channel.basic_consume(
            queue=self.__queue, on_message_callback=self.__on_message, auto_ack=True)

        self.__print_waiting_message()
        self.__channel.start_consuming()

    def __on_message(self, channel, method, properties, body):
        deployment_order_id = body.decode('utf-8')
        print(
            'deployment-order-id={0} was received'.format(deployment_order_id))

        self.__command.build_inventory(deployment_order_id)
        self.__command.deploy()

        self.__print_waiting_message()

    def __print_waiting_message(self):
        print('Waiting for messages. To exit press CTRL+C')


# -----------------------------
# Main
# -----------------------------


def main():
    deploy_queue_listener = DeployQueueListener()
    deploy_queue_listener.start_consuming()


if __name__ == '__main__':
    main()
