import socket
import json
import requests
import threading

# Server address and port number
h = '127.0.0.1'
p = 1373

# Creating the TCP Socket
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind((h, p))
server_socket.listen(4)
print("Server started, waiting for the Username and ICAO code...")

def get_flight_data(arr_icao):
    params = {
        'access_key': 'ea6c1e884b89949a23394c284f90b767',
        'arr_icao': arr_icao,
        'limit': 100
    }
    res = requests.get('http://api.aviationstack.com/v1/flights', params)
    with open('Group_B4.json', 'w') as f:
        json.dump(res.json(), f,indent=3)

    print("The Data is stored in Group_B4.json file \n")
    response = json.load(open('Group_B4.json', ))
    return response

def send(client_socket, flights):
    flights_json = json.dumps(flights)  # Convert flights to a JSON string
    client_socket.sendall(flights_json.encode('ascii'))

# Modify the handle_client_requests function in the server
def handle_client_requests(client_socket, username, response):
    while True:
        try:
            request = client_socket.recv(1024).decode('ascii')
            print(f"Request from {username}: {request} \n")

            if not request:
                break

            if request == 'a':
                flights = arrived_flights(response)
                print("Sending data to", username, "\n")
                send(client_socket, flights)

            elif request == 'b':
                flights = delayed_flights(response)
                print("Sending data to", username, "\n")
                send(client_socket, flights)

            elif request.startswith('c'):
                c_iata = request[1:]  # Extract city IATA from the request
                print(c_iata)
                flights = flights_from_airport(c_iata, response)
                print("Sending data to", username, "\n")
                send(client_socket, flights)

            elif request.startswith('d'):
                f_iata = request[1:] # Extract flight IATA from the request
                print(f_iata)
                flights = get_flight_details(f_iata, response)
                print("Sending data to", username, "\n")
                send(client_socket, flights)

            elif request == 'quit':
                response = json.dumps([])  # Always send a well-formed JSON response
                client_socket.send(response.encode('ascii'))
                print(f"Client {username} is disconnecting... \n")
                break

            else:
                print("Invalid request... \n")

        except ConnectionResetError:
            print(username, " clicked Ctrl+C, so the connection is disconnected ..")
            client_socket.close()
            break
            
        except:
            print("Sorry, something went wrong...")
            print(username, ", the connection will be discontinued... \n")
            client_socket.close()
            break


    client_socket.close()


def arrived_flights(flight_data):
    arrived_f = []
    for flight in flight_data['data']:
        if flight['flight_status'] == 'landed':
            flight_info = {
                'flight_code': str(flight['flight']['iata']),
                'departure_airport': str(flight['departure']['airport']),
                'arrival_time': str(flight['arrival']['scheduled']),
                'arrival_terminal': str(flight['arrival'].get('terminal', 'N/A')),
                'arrival_gate': str(flight['arrival'].get('gate', 'N/A')),
            }
            arrived_f.append(flight_info)
    return arrived_f

def delayed_flights(flight_data):
    delayed_f = []
    for flight in flight_data['data']:
        if flight['flight_status'] == 'landed' and flight['arrival']['delay']:
            flight_info = {
                'flight_code': str(flight['flight']['iata']),
                'departure_airport': str(flight['departure']['airport']),
                'original_departure_time': str(flight['departure']['scheduled']),
                'estimated_time_arrival': str(flight['arrival']['estimated']),
                'delay': str(flight['departure']['delay']),
                'arrival_terminal': str(flight['arrival'].get('terminal', 'N/A')),
                'arrival_gate': str(flight['arrival'].get('gate', 'N/A')),
            }
            delayed_f.append(flight_info)
    return delayed_f

def flights_from_airport(c_iata, flight_data):
    airportflights = []
    for flight in flight_data['data']:
        if flight['departure']['airport'] == c_iata:
            info = {
                'flight_code': str(flight['flight']['iata']),
                'departure_airport': str(flight['departure']['airport']),
                'original_departure_time': str(flight['departure']['scheduled']),
                'estimated_arrival_time': str(flight['arrival']['estimated']),
                'arrival_gate': str(flight['arrival'].get('gate', 'N/A')),
                'status': str(flight['flight_status']),
            }
            airportflights.append(info)
    return airportflights

def get_flight_details(f_iata, flight_data):
    flight_details = {}
    for flight in flight_data['data']:
        if flight['flight']['iata'] == f_iata:
            flight_details = {
                'flight_code': str(flight['flight']['iata']),
                'departure_airport': str(flight['departure']['airport']),
                'departure_terminal': str(flight['departure'].get('terminal', 'N/A')),
                'departure_gate': str(flight['departure'].get('gate', 'N/A')),
                'arrival_terminal': str(flight['arrival']['airport']),
                'arrival_gate': str(flight['arrival'].get('gate', 'N/A')),
                'status': str(flight['flight_status']),
                'scheduled_departure_time': str(flight['departure']['scheduled']),
                'scheduled_arrival_time': str(flight['arrival']['scheduled']),
            }
            break
    return flight_details

def start_server():
    arr_icao = input("enter ICAO code: ")
    response = get_flight_data(arr_icao)
    while True:
        c_socket, client_address = server_socket.accept()
        print(f"Accepted the connection from {client_address}")

        # Receiving Username from the client
        username = c_socket.recv(1024).decode('ascii')
        print("Username:", username)

        # Create a new thread for each client
        client_thread = threading.Thread(target=handle_client_requests, args=(c_socket, username, response))
        client_thread.start()

# Start the server
start_server()
