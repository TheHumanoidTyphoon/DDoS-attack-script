# DDoS Attack Script

This script is a DDoS (Distributed Denial of Service) attack tool that can be used to test the resilience of a network against a DDoS attack. It works by sending a large number of requests to a target server or IP address, with the aim of overwhelming its resources and causing it to become unavailable.

## Requirements:
- `Python 3.x`
- `argparse`
- `socket`
- `concurrent.futures`
- `logging`
- `secrets`
## Usage:
The script can be executed from the command line using the following command:
```python
python3 ddos_attack.py [targets] [port] [fake_ip] [attack_type] [--duration] [--threads]
```
- `targets`: A comma-separated list of target IP addresses.
- `port`: The target port number.
- `fake_ip`: The fake IP address to use in the attack.
- `attack_type`: The type of attack to launch. Options are `TCP_SYN`, `UDP_Flood`, `HTTP_Flood`, and `DNS_Amplification`.
- `--duration`: The duration of the attack in seconds. Default is 60 seconds.
- `--threads`: The maximum number of threads in the pool. Default is 50 threads.
## Rate Limiting
The script implements a simple token bucket rate limiter to prevent the attack from overwhelming the local network. The rate limiter allows a maximum of 10 tokens to be stored in the bucket and releases 1 token per second. Each request consumes 1 token from the bucket, and if no tokens are available, the request is blocked until a token becomes available.

## Logging
The script logs all errors and connection attempts to a file named attack.log in the current working directory. The log file is created if it does not exist, and is appended to if it does exist.

## Example
```python
python ddos_attack.py 192.168.0.1,192.168.0.2,192.168.0.3 80 192.168.0.4 TCP_SYN --duration 120 --threads 100
```
This command launches a `TCP SYN` flood attack against the IP addresses `192.168.0.1`, `192.168.0.2`, and `192.168.0.3`, using port `80` and a fake IP address of `192.168.0.4`. The attack will last for 120 seconds and use a maximum of 100 threads.
