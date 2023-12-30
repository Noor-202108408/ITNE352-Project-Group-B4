import socket
import json
import tkinter as tk
from tkinter import messagebox, simpledialog

# Server's information
S_address = '127.0.0.1'
S_port = 1356

# Connect the client to the server
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect((S_address, S_port))

# Prompt the user for a username
Username = simpledialog.askstring("Username", "Enter your username: ")
client_socket.send(Username.encode('ascii'))

# Create a function to send requests to the server
def send_request(request_type):
    # Send the request type to the server
    client_socket.send(request_type.encode('ascii'))

    # Receive the response from the server
    response = client_socket.recv(4096).decode('ascii')

    # Process and display the flight information
    flights = json.loads(response)
    if not flights:
        messagebox.showinfo('No Flights', 'No flights found. SORRY!')
    else:
        flight_info = ""
        for flight in flights:
            if request_type.lower() == 'a':
                # Arrived flights
                flight_info += f"Flight Code (IATA): {flight['flight']['iata']}\n"
                flight_info += f"Departure Airport: {flight['departure']['airport']}\n"
                flight_info += f"Arrival Time: {flight['arrival']['estimated']}\n"
                flight_info += f"Arrival Terminal: {flight['arrival']['terminal']}\n"
                flight_info += f"Arrival Gate: {flight['arrival']['gate']}\n\n"

            elif request_type.lower() == 'b':
                # Delayed flights
                flight_info += f"Flight Code (IATA): {flight['flight']['iata']}\n"
                flight_info += f"Departure Airport: {flight['departure']['airport']}\n"
                flight_info += f"Departure Time: {flight['departure']['estimated']}\n"
                flight_info += f"Estimated Arrival Time: {flight['arrival']['estimated']}\n"
                flight_info += f"Delay: {flight['arrival']['delay']}\n"
                flight_info += f"Terminal: {flight['arrival']['terminal']}\n"
                flight_info += f"Gate: {flight['arrival']['gate']}\n\n"

            elif request_type.lower() == 'c':
                # All flights coming from a specific city
                c_iata = simpledialog.askstring("City IATA", "Enter city IATA: ")
                client_socket.send(c_iata.encode('ascii'))
                flight_info += f"Flight Code (IATA): {flight['flight']['iata']}\n"
                flight_info += f"Departure Airport: {flight['departure']['airport']}\n"
                flight_info += f"Departure Time: {flight['departure']['estimated']}\n"
                flight_info += f"Estimated Arrival Time: {flight['arrival']['estimated']}\n"
                flight_info += f"Departure Gate: {flight['departure']['gate']}\n"
                flight_info += f"Arrival Gate: {flight['arrival']['gate']}\n"
                flight_info += f"Status: {flight['flight']['status']}\n\n"

            elif request_type.lower() == 'd':
                # Details of a particular flight
                f_iata = simpledialog.askstring("Flight IATA", "Enter flight IATA: ")
                client_socket.send(f_iata.encode('ascii'))
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

# Create a function to handle quitting
def quit():
    # Send the quit request type to the server
    client_socket.send("quit".encode('ascii'))
    # Close the client socket
    client_socket.close()
    # Destroy the GUI window
    window.destroy()

# Create a GUI window
window = tk.Tk()
window.title("Flight Information Client")

# Create a menu
menu= tk.Menu(window)
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

# Run the GUI window
window.mainloop()