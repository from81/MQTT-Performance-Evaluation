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