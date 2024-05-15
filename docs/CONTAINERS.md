# Docker Containers

This project provides a set of Docker containers for various purposes.

## Containers

Working:

- `discord_logger` - A container for running a server that listens for DB updates and runs
- `redis` - A container for running a Redis server.
- `postgres` - A container for running a PostgreSQL database.

## Using Docker Compose

The recommended way to run the containers is with `docker compose`. This method is easier and more efficient than running the containers manually.

### Running the Containers

#### Step 1: Install Docker Compose

Ensure Docker Compose is installed on your system. It usually comes bundled with Docker Desktop for Windows and Mac. For Linux, you might need to install it separately.

#### Step 2: Run the Containers

Run the following command from the root of this repository:

```

docker compose -f containers/docker-compose.yml up -d

```

#### Step 3: Verify the Containers are Running

Run the following command to verify the containers are running:

```

docker ps

```

You should see the following containers running:

- `discord_logger`
- `dispatcher`
- `redis`
- `postgres`
- `health_monitor`

#### All Done!

Your containers are now running and can communicate with each other.

### Stopping the Containers

To stop the containers, run the following command from the root of this repository:

```

docker compose -f containers/docker-compose.yml down

```

### Viewing Logs

To view the logs of a specific container, run the following command:

```

docker compose logs [options] [service_name]

```

`[options]` can include various flags to alter the behavior of the logs command. For example, `-f` or `--follow` to follow the log output (similar to `tail -f`), `-t` or `--timestamps` to show timestamps for each log entry, and `--tail` to limit the number of lines shown.

`[service_name]` is the name of the service you want to view logs for. For example, `discord_logger`, `dispatcher`, or `redis`.

To view the logs of all services, simply omit the `[service_name]` argument.

## Running Manually

It is possible to run the containers manually using the `docker run` command. However, it is recommended to use the `docker compose` command to run the containers.

Manually running the containers is useful for debugging and testing purposes.

### Steps:

NOTE: All steps assume you are running from the root of this repository.

All steps also assume you have Docker installed and running as well as a `.env` file in the root of this repository.

See [`.env` documentation](ENV.md) for more information.

#### Step 1: Create a Docker Network

First, create a custom bridge network. This network will allow containers attached to it to communicate with each other directly. You can create a network with the following command:

```
docker network create compose_network
```

#### Step 2: Build and Run Redis Container on the Custom Network

When you run your Redis container, attach it to the network you just created using the --network option. If your Redis container is already running, you'll need to stop it and start it again on the new network.

Build it:

```
docker build -t redis_image -f containers/redis/Dockerfile .
```

or...

Download it:

```
docker pull ryeager12/discord-parser-bravo:redis
```

Run it:

```
docker run --name my_redis_container -it --network compose_network -p 6379:6379 --env-file .env -v ./database/redis:/data redis_image
```

Replace `my_redis_container` with a name for your Redis container and `compose_network` with the name of your Docker network. The `-p 6379:6379` option is still used to expose Redis to your host for direct access.

#### Step 3: Build and Run The Discord Logger Container on the Same Network

When you run your Redis container, attach it to the network you just created using the --network option. If your Redis container is already running, you'll need to stop it and start it again on the new network.

Build it:

```
docker build -t postgres_image -f containers/postgres/Dockerfile .
```

or...

Download it:

```
docker pull ryeager12/discord-parser-bravo:postgres
```

Run it:

```
docker run --name postgres_container -it --network compose_network -p 5432:5432 --env-file .env -v ./database/postgres:/var/lib/postgresql/data postgres_image
```

Replace `my_redis_container` with a name for your Redis container and `compose_network` with the name of your Docker network. The `-p 6379:6379` option is still used to expose Redis to your host for direct access.

#### Step 4: Build and Run The Discord Logger Container on the Same Network

Now, run your second container (the one that needs to access the Redis server) on the same network. You do not need to publish the Redis port again since the communication will be internal within the Docker network.

Build it:

```
docker build -t discord_logger -f containers/discord_logger/Dockerfile .
```

or...

Download it:

```
docker pull ryeager12/discord-parser-bravo:discord_logger
```

Run it:

```
docker run --name my_other_container -it --network compose_network --env-file .env -v ./config:/app/config discord_logger
```

Replace `my_other_container` with a name for this container and `compose_network` with the name of your Docker network.

#### Step 5: Build and Run The Discord Logger Container on the Same Network

Now, run your second container (the one that needs to access the Redis server) on the same network. You do not need to publish the Redis port again since the communication will be internal within the Docker network.

Build it:

```
docker build -t dispatcher -f containers/dispatcher/Dockerfile .
```

or...

Download it:

```
docker pull ryeager12/discord-parser-bravo:dispatcher
```

Run it:

```
docker run --name my_other_other_container --network compose_network -it --env-file .env -v ./config:/app/config dispatcher
```

Replace `my_other_other_container` with a name for this container and `compose_network` with the name of your Docker network.

#### Step 6: Run the Client Container

Build it:

```
docker build -t example_client -f containers/client/Dockerfile .
```

or...

Download it:

```
docker pull ryeager12/discord-parser-bravo:example_client
```

Run it:

```
docker run --name my_client_container --network compose_network -it --env-file .env example_client
```

#### Step 7: Run the Health Monitor Container

Build it:

```
docker build -t health_monitor -f containers/health_monitor/Dockerfile .
```

or...

Download it:

```
docker pull ryeager12/discord-parser-bravo:health_monitor
```

Run it:

```
docker run --name my_health_monitor_container --network compose_network -it --env-file .env health_monitor
```

#### All Done!

Your containers are now running on the same network and can communicate with each other.

Here are the commands in a more readable format:

```
docker build -t redis_image -f containers/redis/Dockerfile .
docker build -t discord_logger -f containers/discord_logger/Dockerfile .
docker build -t dispatcher -f containers/dispatcher/Dockerfile .
docker build -t example_client -f containers/client/Dockerfile .
docker build -t postgres_image -f containers/postgres/Dockerfile .
docker build -t health_monitor -f containers/health_monitor/Dockerfile .
```

IMPORTANT: the `redis_image` should be set as the `REDIS_HOST` variable in the `.env` file.

```

...
REDIS_HOST=redis_image
...

```

As a shortcut, you can do all of this as a build command as well:

```

make docker_build

```

Stop and remove previous containers:

```

docker network disconnect discord_parser_network redis_container
docker network disconnect discord_parser_network discord_logger_container
docker network disconnect discord_parser_network dispatcher_py_container
docker network disconnect discord_parser_network example_client_container
docker network disconnect discord_parser_network postgres_container
docker network disconnect discord_parser_network health_monitor_container
docker network rm discord_parser_network

docker stop redis_container
docker stop discord_logger_container
docker stop dispatcher_py_container
docker stop example_client_container
docker stop postgres_container
docker stop health_monitor_container

docker rm redis_container
docker rm discord_logger_container
docker rm dispatcher_py_container
docker rm example_client_container
docker rm postgres_container
docker rm health_monitor_container


```

Run these in separate terminals or in the background by adding the `-d` option to the `docker run` command.

```

docker network create discord_parser_network
docker run --name redis_container -it --network discord_parser_network -p 6379:6379 --env-file .env -v ./database/redis:/data redis_image
docker run --name discord_logger_container -it --network discord_parser_network --env-file .env -v ./config:/app/config discord_logger
docker run --name dispatcher_py_container -it --network discord_parser_network --env-file .env -v ./config:/app/config dispatcher
docker run --name example_client_container -it --network discord_parser_network --env-file .env example_client
docker run --name postgres_container -it --network discord_parser_network --env-file .env -v ./database/postgres:/var/lib/postgresql/data -p 5432:5432 postgres_image
docker run --name health_monitor_container -it --network discord_parser_network --env-file .env health_monitor

```
