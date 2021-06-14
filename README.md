# About

Project for COMP6331 Computer Networks at ANU.

The aim of this project is to deploy a MQTT broker and to test the MQTT network using various levels of QoS and inter-message delays.

Data Analysis included.
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

# Design

- `controller`
    1. Uses `clinet.loop_forever()` to run the main client indefinitely.
    2. Every time `request/delay` message is received, it launches a publisher that publishes counter at specified delay and QoS for 120 seconds as an asynchronous coroutine.
- `analyzer`
    - For each combination of QoS and delay:
        - Subscribe to the next topic.
        - Publishes request to update QoS and delay as a pair of messages, one for updating QoS and another for updating delay. These messages will reach the `controller` via the broker, and when the `controller` receives the messages, it will start a new publisher.
        - The `analyzer` will listen on the topic and collect data for 120 seconds.

# Observation

Below is the table showing the number of messages lost and the loss rate for various QoS and delay levels.
- Message loss rate is very high (nearly 100%) for QoS of level 1 and 2 for delay of 0, but loss rate is 0 for QoS 0 delay 0.
- Part of this can be attributed to the fact that I'm using EC2 instance in Sydney, from Sydney. Even with QoS of 0, the number of hops required between my machine and EC2 are so small that messages (apparently) do not get lost. As such, when using QoS of 1 or 2 with delay of 0, the next messages arrive before completing the transmission of the previous message. This is because QoS of level 1 and 2 requires minimum of 2-4 messages, while QoS of level 0 requires only 1 message.
- We can verify the assumption by looking at `counter/2/10` which had loss rate of 27.7%. This means that at QoS of 2 and delay of 10, transmission of messages **usually** completes before the transmission of the next one begins.


|    | topic         |   n_msg_lost |   msg_loss_rate |
|---:|:--------------|-------------:|----------------:|
|  0 | counter/0/0   |            0 |        0        |
|  1 | counter/0/10  |            0 |        0        |
|  2 | counter/0/100 |            0 |        0        |
|  3 | counter/0/20  |            0 |        0        |
|  4 | counter/0/50  |            0 |        0        |
|  5 | counter/0/500 |            0 |        0        |
|  6 | counter/1/0   |       378450 |        0.980689 |
|  7 | counter/1/10  |            0 |        0        |
|  8 | counter/1/100 |            0 |        0        |
|  9 | counter/1/20  |            0 |        0        |
| 10 | counter/1/50  |            0 |        0        |
| 11 | counter/1/500 |            0 |        0        |
| 12 | counter/2/0   |       257657 |        0.976243 |
| 13 | counter/2/10  |         2133 |        0.277662 |
| 14 | counter/2/100 |            0 |        0        |
| 15 | counter/2/20  |            0 |        0        |
| 16 | counter/2/50  |            0 |        0        |
| 17 | counter/2/500 |            0 |        0        |