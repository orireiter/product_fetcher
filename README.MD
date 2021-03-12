# Amazon+Walmart Product Fetcher

A Backend web-service that retrieves info about products from Amazon and Walmart.

## Installation
The easiest way would be to cd into ./docker/docker-compose and execute "docker-compose up".\
It is ___VERY___ recommended the check the configuration files in that same dir beforehand.
```cmd
cd ./docker/docker-compose
docker-compose up
```

## Usage
After the service is up, you may use the two endpoints:\
__http://localhost/fetch/source/product_ID__
* This endpoint will fetch info about a product by the ID and source given.\
For example: _http://localhost/fetch/amazon/B07DQWT15Y_
* This endpoint only serves GET requests. The source field may only be _amazon_ OR _walmart_. The product ID can ONLY contain numbers and capital letters.

__http://localhost/filter/source?gte=int&lte=int__
* This endpoint will retrieve a list of product from the given source and within the price range specified by him.\
For example: _http://localhost/filter/amazon?gte=5&lte=20_
* This endpoint only serves GET requests. The source field may only be _amazon_ OR _walmart_. The __gte__ parameter represents the lowest price in the range, whereas __lte__ represents the highest. Both included. ___BOTH PARAMETERS MUST BE GIVEN.___

## Architecture
![Architecture_picture.jpg](https://github.com/orireiter/YBL_product_service/blob/main/etc/arch.jpg?raw=true)\
![Architecture_picture_rabbitmq.jpg](https://github.com/orireiter/YBL_product_service/blob/main/etc/rabbit_arch.jpg?raw=true)\
This service is made of a few mini-services:

### 1) MongoDB -
A NoSQL database. It is used to store product info, in order to fetch it faster the next time it same product is asked for.

### 2) RabbitMQ -
A message broker that transfers messages between the mini-services.

### 3) Web Server - 
A mini-service that serves the endpoints pointed above. Upon a Valid GET request, it will send a message through RabbitMQ to a DB Reader. It is written in python+flask

### 4) DB Reader By ID - 
A mini-service that consumes messages from RabbitMQ and queries the DB for a product with the given source and ID. It either answers the web server which will answer the client, or, if the ID isn't in the DB, will redirect the message to an amazon/walmart remote product fetcher.

### 5) Amazon Product Fetcher -
A mini-service that consumes messages from RabbitMQ and queries the an amazon remote API for a product with the given ID. It will Then return the product info to the client (through the web service), and also send it to a DB Writer mini-service.

### 6) DB Writer - 
A mini-service that consumes messages from RabbitMQ and inserts records into the DB.

### 7) Walmart Product Fetcher -
A mini-service that consumes messages from RabbitMQ and queries a Walmart remote API for a product with the given ID. It will Then return the product info to the client (through the web service), and also send it to a DB Writer mini-service.

### 8) Walmart Header Fetcher -
A mini-service that fetches headers needed to interact with Walmart's API every given time, and writes them into a file shared with the main Walmart fetcher.

### 9) DB Reader By Filter - 
A mini-service that consumes messages from RabbitMQ and queries the DB for a product with the given source and price range. It answers the web server which will answer the client.

## RabbitMQ Routing, Queues, and Exchanges
In version 0.0.2, the web server messages the db readers, and depending on their answer, continues to message the fetchers. Then, before responding to the client, it sends the info to be written in the DB.\
In version 0.0.5+, the web server messages the db readers, which answer or redirect the message to the fetchers if there is no such ID in the DB.\
The fetchers then send the answer through an exchange to the web server that responds to the client.
That exchange is a topic exchange and the db writer(s) also receive ANY message sent to it, to put less work on the web server.

## Configuration
There are 3 configuration files in this project. It's highly recommended to check all of them out before running this service.

### 1) docker-compose.yml - 
The most-important-to-know fields in this file are the replicas which will let replicate a container, and container_name, which should fit the RabbitMQ and MongoDB names in config.yml's hosts which will be explained later.

### 2) config.yml - 
This file contains many parameters the containers use.\
__KEYS SHOULDN'T BE CHANGED.__

RabbitMQ values' require the name given in container_name in docker-compose.yml, and set queue and exchange names.

MongoDB values' require the name given in container_name in docker-compose.yml, and set DB and Collection names, as well as a TTL in seconds for the records (since data ages).

Amazon values' set the amazon api to request from when the info isn't in the DB yet, a list of servers which this container depends on (each object in this list is a pair of a host and a port), and names of keys to keep (so only these field will be registered to the DB).

Walmart values' are the same as Amazon's, with an additional API that retrieves headers necessary to query Walmart's API, a file to write these headers into, and the interval of headers fetching.

The rest only contain a list of services these containers depend on.

### 3) config.json - 
A configuration file for nginx/unit (which serves the web-server), for more info on that check their official docs.