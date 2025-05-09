import random
import hashlib
import matplotlib.pyplot as plt
import time
import pandas as pd # type: ignore

class Vehicle:
    def _init_(self, vehicle_id, speed, position):
        self.id = vehicle_id
        self.speed = speed
        self.position = position
        self.salt = "vanet" + str(random.random())  # Add a salt

    def move(self, dt):
        self.position = (self.position[0] + self.speed * dt * random.uniform(-0.1, 1.1),
                         self.position[1] + self.speed * dt * random.uniform(-0.1, 1.1))

    def check_collision(self, other, threshold=1):
        distance = ((self.position[0] - other.position[0]) ** 2 +
                    (self.position[1] - other.position[1]) ** 2) ** 0.5
        return distance < threshold

    def generate_message(self):
        message = {
            "vehicle_id": self.id,
            "speed": self.speed,
            "position": self.position,
        }
        return message, self.hash_message(message)

    def hash_message(self, message):
        message_bytes = str(message).encode()
        hashes = {}
        start_time = time.time()
        hashes["sha256"] = hashlib.sha256(message_bytes + self.salt.encode()).hexdigest()
        hashes["sha256_time"] = time.time() - start_time
        start_time = time.time()
        hashes["md5"] = hashlib.md5(message_bytes + self.salt.encode()).hexdigest()
        hashes["md5_time"] = time.time() - start_time
        start_time = time.time()
        hashes["sha1"] = hashlib.sha1(message_bytes + self.salt.encode()).hexdigest()
        hashes["sha1_time"] = time.time() - start_time
        start_time = time.time()
        hashes["blake2b"] = hashlib.blake2b(message_bytes + self.salt.encode()).hexdigest()
        hashes["blake2b_time"] = time.time() - start_time
        start_time = time.time()
        hashes["sha3_256"] = hashlib.sha3_256(message_bytes + self.salt.encode()).hexdigest()
        hashes["sha3_256_time"] = time.time() - start_time
        return hashes

    def check_integrity(self, message, hashes):
        for hash_type, hash_value in hashes.items():
            if hash_type in ["sha256", "md5", "sha1", "blake2b", "sha3_256"]:
                if hash_value!= self.hash_message(message)[hash_type]:
                    return False
        return True

    def receive_message(self, message, hashes):
        print(f"Vehicle {self.id} received message from {message['vehicle_id']}: {message}")
        print(f"Received hashes: {hashes}")
        if self.check_integrity(message, hashes):
            print("Message integrity is valid.")
        else:
            print("Message integrity is NOT valid!")

def simulate(vehicles, dt, num_steps):
    hash_times = {"sha256": [], "md5": [], "sha1": [], "blake2b": [], "sha3_256": []}
    for _ in range(num_steps):
        for vehicle in vehicles:
            vehicle.move(dt)
            collisions = [other for other in vehicles if vehicle!= other and vehicle.check_collision(other)]
            if collisions:
                print(f"Collision detected between vehicle {vehicle.id} and: {', '.join(other.id for other in collisions)}")

            message, hashes = vehicle.generate_message()
            for other in vehicles:
                if hasattr(other, 'receive_message'):
                    other.receive_message(message.copy(), hashes.copy())
            for hash_type, hash_time in hashes.items():
                if hash_type.endswith("_time"):
                    hash_times[hash_type[:-5]].append(hash_time)

    # Prepare data for Pandas boxplot
    hash_data = []
    for hash_type, times in hash_times.items():
        for time in times:
            hash_data.append({"hash_type": hash_type, "time": time})

    # Convert hash_data to a DataFrame
    hash_df = pd.DataFrame(hash_data)

    # Create a boxplot using Pandas
    hash_df.boxplot(column="time", by="hash_type", showmeans=True)
    plt.title("Hash Generation Times")
    plt.ylabel("Time (s)")
    plt.xlabel("Hash Function")
    plt.xticks(rotation=45)  # Rotate hash type labels for better readability
    plt.show()

def plot_speeds(vehicles, num_steps, dt):
    times = list(range(num_steps))
    speeds = {vehicle.id: [] for vehicle in vehicles}
    for i in range(num_steps):
        for vehicle in vehicles:
            vehicle.move(dt)
            speeds[vehicle.id].append(vehicle.speed)
        collisions = [other for other in vehicles if vehicle!= other and vehicle.check_collision(other)]
        if collisions:
            print(f"Collision detected between vehicle {vehicle.id} and: {', '.join(other.id for other in collisions)}")

    # Create a pandas DataFrame
    speeds_df = pd.DataFrame(speeds, index=times)

    # Plot speeds using matplotlib
    speeds_df.plot(figsize=(10, 5), title="Vehicle Speeds Over Time", legend=True)
    plt.xlabel("Time")
    plt.ylabel("Speed")
    plt.show()

def plot_positions(vehicles, num_steps, dt):
    positions = {vehicle.id: [] for vehicle in vehicles}
    for i in range(num_steps):
        for vehicle in vehicles:
            vehicle.move(dt)
            positions[vehicle.id].append(vehicle.position)
        collisions = [other for other in vehicles if vehicle!= other and vehicle.check_collision(other)]
        if collisions:
            print(f"Collision detected between vehicle {vehicle.id} and: {', '.join(other.id for other in collisions)}")

    # Create a pandas DataFrame
    positions_df = pd.DataFrame(positions)

    # Plot positions using matplotlib
    positions_df.apply(pd.Series.explode).plot.scatter(x=0, y=1, figsize=(10, 5), title="Vehicle Positions Over Time", legend=True)
    plt.xlabel("X Position")
    plt.ylabel("Y Position")
    plt.show()

vehicle1 = Vehicle("V1", 65, (0, 0))
vehicle2 = Vehicle("V2", 50, (10, 20))
vehicle3 = Vehicle("V3", 35, (30, 50))
vehicle4 = Vehicle("V4", 20, (10, 50))
vehicle5 = Vehicle("V5", 95, (30, 10))
vehicle6 = Vehicle("V6", 70, (70, 10))

# Valid message
message, hashes = vehicle1.generate_message()
vehicle2.receive_message(message, hashes.copy())

# Invalid message (tampered speed)
tampered_message = message.copy()
tampered_message["speed"] = 100
vehicle2.receive_message(tampered_message, hashes.copy())

# Valid message
message, hashes = vehicle3.generate_message()
vehicle4.receive_message(message, hashes.copy())

# Invalid message (tampered speed)
tampered_message = message.copy()
tampered_message["speed"] = 100
vehicle4.receive_message(tampered_message, hashes.copy())

# Simulate hash generation times
simulate([vehicle1, vehicle2], 0.1, 1000)

# Plot speeds
plot_speeds([vehicle1, vehicle2], 1000, 2000)
            
# Plot positions
plot_positions([vehicle1, vehicle2], 1000, 0.1)

# Simulate hash generation times
simulate([vehicle3, vehicle4], 0.1, 1000)

# Plot speeds
plot_speeds([vehicle3, vehicle4], 1000, 2000)
            
# Plot positions
plot_positions([vehicle3, vehicle4], 1000, 0.1)
