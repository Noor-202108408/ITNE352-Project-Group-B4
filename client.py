import socket
import json
import tkinter as tk
from tkinter import messagebox, simpledialog

# Server's information
S_address = '127.0.0.1'
S_port = 1373

# Connect the client to the server
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect((S_address, S_port))

# Prompt the user for a username
Username = simpledialog.askstring("Username", "Enter your username: ")
client_socket.send(Username.encode('ascii'))

# Create a function to handle response
def handle_response(request_type, response):
        # Print the raw response for debugging
    print("Raw Response:", repr(response))

    try:
        flights = json.loads(response)
    except json.JSONDecodeError as e:
        # Print the exception for debugging
        print("JSON Decode Error:", e)
        messagebox.showerror('Error', 'Error decoding server response.')
        return

    if not flights:
        messagebox.showinfo('No Flights', 'No flights found. SORRY!')
    else:
        flight_info = ""
        for flight in flights:
            if request_type.lower() == 'a':
                # Arrived flights
                flight_info += f"Flight Code (IATA): {flight['flight_code']}\n"
                flight_info += f"Departure Airport: {flight['departure_airport']}\n"
                flight_info += f"Arrival Time: {flight['arrival_time']}\n"
                flight_info += f"Arrival Terminal: {flight['arrival_terminal']}\n"
                flight_info += f"Arrival Gate: {flight['arrival_gate']}\n\n"

            elif request_type.lower() == 'b':
                # Delayed flights
                flight_info += f"Flight Code (IATA): {flight['flight_code']}\n"
                flight_info += f"Departure Airport: {flight['departure_airport']}\n"
                flight_info += f"Departure Time: {flight['original_departure_time']}\n"
                flight_info += f"Estimated Arrival Time: {flight['estimated_time_arrival']}\n"
                flight_info += f"Delay: {flight['delay']}\n"
                flight_info += f"Terminal: {flight['arrival_terminal']}\n"
                flight_info += f"Gate: {flight['arrival_gate']}\n\n"

            elif request_type.lower() == 'c':
                # All flights coming from a specific city
                city_iata = simpledialog.askstring("City IATA", "Enter city IATA: ")
                if city_iata:
                    send_request(f"c{city_iata}")

                    flight_info += f"Flight Code (IATA): {flight['flight']['iata']}\n"
                    flight_info += f"Departure Airport: {flight['departure']['airport']}\n"
                    flight_info += f"Departure Time: {flight['departure']['estimated']}\n"
                    flight_info += f"Estimated Arrival Time: {flight['arrival']['estimated']}\n"
                    flight_info += f"Departure Gate: {flight['departure']['gate']}\n"
                    flight_info += f"Arrival Gate: {flight['arrival']['gate']}\n"
                    flight_info += f"Status: {flight['flight']['status']}\n\n"

            elif request_type.lower() == 'd':
                # Details of a particular flight
                flight_iata = simpledialog.askstring("Flight IATA", "Enter flight IATA: ")
                if flight_iata:
                    send_request(f"d{flight_iata}")

                    flight_info += f"Flight Code (IATA): {flight['flight']['iata']}\n"
                    flight_info += f"Departure Airport: {flight['departure']['airport']}\n"
                    flight_info += f"Departure Gate: {flight['departure']['gate']}\n"
                    flight_info += f"Departure Terminal: {flight['departure']['terminal']}\n"
                    flight_info += f"Arrival Airport: {flight['arrival']['airport']}\n"
                    flight_info += f"Arrival Gate: {flight['arrival']['gate']}\n"
                    flight_info += f"Arrival Terminal: {flight['arrival']['terminal']}\n"
                    flight_info += f"Status: {flight['flight']['status']}\n"
                    flight_info += f"Scheduled Departure Time: {flight['departure']['scheduled']}\n"
                    flight_info += f"Scheduled Arrival Time: {flight['arrival']['scheduled']}\n\n"

        messagebox.showinfo('Flight Information', flight_info)

def send_request(request_type, data=None):
    if request_type.lower() not in ('c', 'd'):
        # Send the request type to the server
        client_socket.send(request_type.encode('ascii'))

        # Receive the response from the server
        response = ""
        while True:
            chunk = client_socket.recv(4096).decode('ascii')
            if not chunk:
                break
            response += chunk
            try:
                json.loads(response)  # Attempt to parse the JSON
                break  # Break if JSON parsing succeeds
            except json.JSONDecodeError:
                continue  # Continue receiving until a complete JSON is received

        # Handle the response
        handle_response(request_type, response)
    
    elif request_type.lower() in ('c'):
        data= input("Enter the city code: ")
        client_socket.send((request_type + data).encode('ascii'))

        response = ""
        while True:
            chunk = client_socket.recv(4096).decode('ascii')
            if not chunk:
                break
            response += chunk
            try:
                json.loads(response)  # Attempt to parse the JSON
                break  # Break if JSON parsing succeeds
            except json.JSONDecodeError:
                continue  # Continue receiving until a complete JSON is received

        # Handle the response
        handle_response(request_type, response)

    elif request_type.lower() in ('d'):
        data= input("Enter the flight IATA code: ")
        client_socket.send((request_type + data).encode('ascii'))

        response = ""
        while True:
            chunk = client_socket.recv(4096).decode('ascii')
            if not chunk:
                break
            response += chunk
            try:
                json.loads(response)  # Attempt to parse the JSON
                break  # Break if JSON parsing succeeds
            except json.JSONDecodeError:
                continue  # Continue receiving until a complete JSON is received

        # Handle the response
        handle_response(request_type, response)    

# Updated quit function to send a formal quit signal to the server
def quit():
    client_socket.send("quit".encode('ascii'))
    client_socket.shutdown(socket.SHUT_RDWR)  # Send shutdown signal to the socket
    client_socket.close()
    window.destroy()

# Create a GUI window
window = tk.Tk()
window.title("Flight Information Client")

# Create a menu
menu = tk.Menu(window)
window.config(menu=menu)

# Create a submenu for request types
request_menu = tk.Menu(menu)
menu.add_cascade(label="Request", menu=request_menu)
request_menu.add_command(label="Arrived Flights", command=lambda: send_request('a'))
request_menu.add_command(label="Delayed Flights", command=lambda: send_request('b'))
request_menu.add_command(label="Flights from a City", command=lambda: send_request('c'))
request_menu.add_command(label="Flight Details", command=lambda: send_request('d'))


# Create a quit button
quit_button = tk.Button(window, text="Quit", command=quit)
quit_button.pack()

try:
    window.mainloop()

except KeyboardInterrupt:
    print("\nPressed Ctrl + C, Cleaning up!")
    quit()  # Call the quit function to ensure proper cleanup on Ctrl+C
