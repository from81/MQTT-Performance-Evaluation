# About

Project for COMP6331 Computer Networks at ANU.

The aim of this project is to deploy a MQTT broker and to test the MQTT network using various levels of QoS and inter-message delays.

Data Analysis included.

# Design

- `controller`
    1. Uses `clinet.loop_forever()` to run the main client indefinitely.
    2. Every time `request/delay` message is received, it launches a publisher that publishes counter at specified delay and QoS for 120 seconds as an asynchronous coroutine.
- `analyzer`
    - For each combination of QoS and delay:
        - Subscribe to the next topic.
        - Publishes request to update QoS and delay as a pair of messages, one for updating QoS and another for updating delay. These messages will reach the `controller` via the broker, and when the `controller` receives the messages, it will start a new publisher.
        - The `analyzer` will listen on the topic and collect data for 120 seconds.
# Setup

- Follow [this setup guide](https://www.instructables.com/How-to-Setup-Mosquitto-MQTT-on-AWS/)
    - Make sure to retain the `.pem` file, which will be needed to `ssh` into the EC2 instance.
- To `ssh` into EC2 instance
    - `ssh -i mqtt_aws.pem ubuntu@ec2-xx-xx-xx-xx.ap-southeast-2.compute.amazonaws.com`
- Subscribe to $SYS topics from local terminal to check that connection to broker can be established.
    - `mosquitto_sub -v -t '$SYS/#' -h xx.xx.xx.xx -u <username> -P <passpord> -i <client_id>`
- If the above works, proceed to the following steps.
    1. Run `cp env_template.json env.json`.
    2. Fill out the `env.json` file.
    3. Run `python controller.py`.
    4. In a second terminal/shell, run `python analyzer.py`.