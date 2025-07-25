import sqlite3

# Database Class
class Database:
    def __init__(self):
        self.conn = sqlite3.connect('hospital.db')
        self.cursor = self.conn.cursor()
        self.init_db()

    def init_db(self):
    # Create tables if they don't exist
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS Doctors (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT, specialty TEXT)''')
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS Patients (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT, age INTEGER, room_number INTEGER)''')
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS Rooms (room_number INTEGER PRIMARY KEY, patient_name TEXT)''')
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS Appointments (id INTEGER PRIMARY KEY AUTOINCREMENT, patient_name TEXT, doctor_name TEXT, date TEXT)''')
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS MedicineStock (medicine_name TEXT PRIMARY KEY, quantity INTEGER)''')
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS LabStock (item_name TEXT PRIMARY KEY, quantity INTEGER)''')
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS Payments (
                                id INTEGER PRIMARY KEY AUTOINCREMENT,
                                patient_name TEXT,
                                amount REAL,
                                payment_method TEXT,
                                date TEXT
                            )''')
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS Billing (
                                id INTEGER PRIMARY KEY AUTOINCREMENT,
                                patient_name TEXT,
                                doctor_fee REAL,
                                room_charge REAL,
                                medicine_charge REAL,
                                lab_charge REAL,
                                total_amount REAL,
                                date TEXT
                            )''')

        self.conn.commit()

        
        # Insert default medicines if the MedicineStock table is empty
        default_medicines = [('Paracetamol', 100), ('Ibuprofen', 50), ('Aspirin', 75)]
        for medicine in default_medicines:
            self.cursor.execute("INSERT OR IGNORE INTO MedicineStock (medicine_name, quantity) VALUES (?, ?)", medicine)

        self.conn.commit()

    def execute(self, query, params=()):
        self.cursor.execute(query, params)
        self.conn.commit()

    def fetch_all(self, query, params=()):
        self.cursor.execute(query, params)
        return self.cursor.fetchall()

    def fetch_one(self, query, params=()):
        self.cursor.execute(query, params)
        return self.cursor.fetchone()

    def close(self):
        self.conn.close()
# Billing Class
class Billing:
    def __init__(self, db):
        self.db = db

    def generate_bill(self):
        patient_name = input("Enter Patient's Name: ")
        
        # Fetch services details
        doctor_fee = float(input("Enter Doctor's Fee: "))
        room_charge = float(input("Enter Room Charge: "))
        medicine_charge = float(input("Enter Medicine Charge: "))
        lab_charge = float(input("Enter Lab Charge: "))

        # Calculate total amount
        total_amount = doctor_fee + room_charge + medicine_charge + lab_charge

        # Record the billing
        date = input("Enter Billing Date (YYYY-MM-DD): ")
        self.db.execute(
            '''INSERT INTO Billing (patient_name, doctor_fee, room_charge, medicine_charge, lab_charge, total_amount, date)
               VALUES (?, ?, ?, ?, ?, ?, ?)''',
            (patient_name, doctor_fee, room_charge, medicine_charge, lab_charge, total_amount, date)
        )
        
        print(f"Bill Generated for {patient_name}")
        print(f"Total Amount: {total_amount}")

    def display_bill(self):
        patient_name = input("Enter Patient's Name to View Bill: ")
        bill = self.db.fetch_one("SELECT * FROM Billing WHERE patient_name = ?", (patient_name,))
        
        if bill:
            print("\n------- Bill Details -------")
            print(f"Patient Name   : {bill[1]}")
            print(f"Doctor Fee     : {bill[2]}")
            print(f"Room Charge    : {bill[3]}")
            print(f"Medicine Charge: {bill[4]}")
            print(f"Lab Charge     : {bill[5]}")
            print(f"Total Amount   : {bill[6]}")
            print(f"Date           : {bill[7]}")
            print("----------------------------\n")
        else:
            print("No bill found for the specified patient.")

    def display_all_bills(self):
        bills = self.db.fetch_all("SELECT * FROM Billing")
        if bills:
            for bill in bills:
                print(f"ID: {bill[0]}, Patient: {bill[1]}, Total: {bill[6]}, Date: {bill[7]}")
        else:
            print("No billing records available.")

# Payment Class
class Payment:
    def __init__(self, db):
        self.db = db

    def add_payment(self):
        patient_name = input("Enter Patient's Name: ")
        amount = float(input("Enter Payment Amount: "))
        payment_method = input("Enter Payment Method (Cash, Card, Insurance): ")
        date = input("Enter Payment Date (YYYY-MM-DD): ")
        
        self.db.execute("INSERT INTO Payments (patient_name, amount, payment_method, date) VALUES (?, ?, ?, ?)",
                        (patient_name, amount, payment_method, date))
        print(f"Payment of {amount} for {patient_name} recorded successfully.")

    def display_all_payments(self):
        payments = self.db.fetch_all("SELECT * FROM Payments")
        if payments:
            for payment in payments:
                print(f"ID: {payment[0]}, Patient: {payment[1]}, Amount: {payment[2]}, Method: {payment[3]}, Date: {payment[4]}")
        else:
            print("No payment records found.")

    def search_payment(self):
        patient_name = input("Enter Patient's Name to Search Payments: ")
        payments = self.db.fetch_all("SELECT * FROM Payments WHERE patient_name = ?", (patient_name,))
        if payments:
            for payment in payments:
                print(f"ID: {payment[0]}, Amount: {payment[2]}, Method: {payment[3]}, Date: {payment[4]}")
        else:
            print("No payments found for the specified patient.")

# Doctor Class
class Doctor:
    def __init__(self, db):
        self.db = db

    def add(self):
        name = input("Enter Doctor's Name: ")
        specialty = input("Enter Doctor's Specialty: ")
        self.db.execute("INSERT INTO Doctors (name, specialty) VALUES (?, ?)", (name, specialty))
        print(f"Doctor {name} added.")

    def remove(self):
        doctor_name = input("Enter Doctor's Name to Remove: ")
        self.db.execute("DELETE FROM Doctors WHERE name = ?", (doctor_name,))
        print(f"Doctor {doctor_name} removed.")

    def display_all(self):
        doctors = self.db.fetch_all("SELECT * FROM Doctors")
        for doc in doctors:
            print(f"Dr. {doc[1]}, Specialty: {doc[2]}")

# Patient Class
class Patient:
    def __init__(self, db):
        self.db = db

    def add(self):
        name = input("Enter Patient's Name: ")
        age = int(input("Enter Patient's Age: "))
        self.db.execute("INSERT INTO Patients (name, age) VALUES (?, ?)", (name, age))
        print(f"Patient {name} added.")

    def remove(self):
        patient_name = input("Enter Patient's Name to Remove: ")
        self.db.execute("DELETE FROM Patients WHERE name = ?", (patient_name,))
        self.db.execute("UPDATE Rooms SET patient_name = NULL WHERE patient_name = ?", (patient_name,))
        print(f"Patient {patient_name} removed.")

    def display_all(self):
        patients = self.db.fetch_all("SELECT * FROM Patients")
        for pat in patients:
            print(f"{pat[1]}, Age: {pat[2]}, Room: {pat[3]}")

# Room Class
class Room:
    def __init__(self, db):
        self.db = db

    def add(self):
        room_number = int(input("Enter Room Number: "))
        self.db.execute("INSERT INTO Rooms (room_number) VALUES (?)", (room_number,))
        print(f"Room {room_number} added.")

    def remove(self):
        room_number = int(input("Enter Room Number to Remove: "))
        self.db.execute("DELETE FROM Rooms WHERE room_number = ?", (room_number,))
        print(f"Room {room_number} removed.")

    def assign(self):
        patient_name = input("Enter Patient's Name: ")
        room_number = int(input("Enter Room Number to Assign: "))
        self.db.execute("UPDATE Patients SET room_number = ? WHERE name = ?", (room_number, patient_name))
        self.db.execute("UPDATE Rooms SET patient_name = ? WHERE room_number = ?", (patient_name, room_number))
        print(f"Patient {patient_name} assigned to Room {room_number}.")

    def display_all(self):
        rooms = self.db.fetch_all("SELECT * FROM Rooms")
        for room in rooms:
            patient = room[1] if room[1] else "No Patient Assigned"
            print(f"Room {room[0]}: {patient}")

# Appointment Class
class Appointment:
    def __init__(self, db):
        self.db = db

    def schedule(self):
        patient_name = input("Enter Patient's Name: ")
        doctor_name = input("Enter Doctor's Name: ")
        date = input("Enter Appointment Date (YYYY-MM-DD): ")
        self.db.execute("INSERT INTO Appointments (patient_name, doctor_name, date) VALUES (?, ?, ?)", 
                        (patient_name, doctor_name, date))
        print(f"Appointment scheduled for {patient_name} with Dr. {doctor_name} on {date}.")

    def remove(self):
        appointment_id = int(input("Enter Appointment ID to Remove: "))
        self.db.execute("DELETE FROM Appointments WHERE id = ?", (appointment_id,))
        print(f"Appointment ID {appointment_id} removed.")

    def display_all(self):
        appointments = self.db.fetch_all("SELECT * FROM Appointments")
        for app in appointments:
            print(f"Appointment: {app[1]} with Dr. {app[2]} on {app[3]}")

# Medicine Stock Class
class MedicineStock:
    def __init__(self, db):
        self.db = db

    def add(self):
        medicine_name = input("Enter Medicine Name to Add/Update: ").strip()
        quantity = int(input("Enter Quantity to Add: "))
        result = self.db.fetch_one("SELECT quantity FROM MedicineStock WHERE medicine_name = ?", (medicine_name,))
        
        if result:
            self.db.execute("UPDATE MedicineStock SET quantity = quantity + ? WHERE medicine_name = ?", (quantity, medicine_name))
            print(f"Updated stock of {medicine_name} by {quantity} units.")
        else:
            self.db.execute("INSERT INTO MedicineStock (medicine_name, quantity) VALUES (?, ?)", (medicine_name, quantity))
            print(f"Added new medicine {medicine_name} with {quantity} units.")

    def remove(self):
        medicine_name = input("Enter Medicine Name to Remove: ").strip()
        quantity = int(input("Enter Quantity to Remove: "))
        result = self.db.fetch_one("SELECT quantity FROM MedicineStock WHERE medicine_name = ?", (medicine_name,))
        
        if result and result[0] >= quantity:
            self.db.execute("UPDATE MedicineStock SET quantity = quantity - ? WHERE medicine_name = ?", (quantity, medicine_name))
            print(f"Removed {quantity} units of {medicine_name}.")
        else:
            print("Insufficient stock or not found.")

    def buy(self):
        stock = self.db.fetch_all("SELECT * FROM MedicineStock")
        if stock:
            print("Available Medicines:")
            for med in stock:
                print(f"{med[0]}: {med[1]} units")
        else:
            print("No medicines available.")
            return

        medicine_name = input("Enter Medicine Name: ").strip()
        quantity = int(input("Enter Quantity: "))
        result = self.db.fetch_one("SELECT quantity FROM MedicineStock WHERE medicine_name = ?", (medicine_name,))
        
        if result and result[0] >= quantity:
            self.db.execute("UPDATE MedicineStock SET quantity = quantity - ? WHERE medicine_name = ?", (quantity, medicine_name))
            print(f"Sold {quantity} units of {medicine_name}.")
        else:
            print("Insufficient stock or medicine not found.")

    def display_all(self):
        stock = self.db.fetch_all("SELECT * FROM MedicineStock")
        for med in stock:
            print(f"{med[0]}: {med[1]} units")

# Lab Stock Class
class LabStock:
    def __init__(self, db):
        self.db = db

    def add(self):
        item_name = input("Enter Lab Item Name to Add: ").strip()
        quantity = int(input("Enter Quantity to Add: "))
        self.db.execute("INSERT INTO LabStock (item_name, quantity) VALUES (?, ?) ON CONFLICT(item_name) DO UPDATE SET quantity = quantity + ?",
                        (item_name, quantity, quantity))
        print(f"Added {quantity} units of {item_name}.")

    def remove(self):
        item_name = input("Enter Lab Item Name to Remove: ").strip()
        quantity = int(input("Enter Quantity to Remove: "))
        result = self.db.fetch_one("SELECT quantity FROM LabStock WHERE item_name = ?", (item_name,))
        
        if result and result[0] >= quantity:
            self.db.execute("UPDATE LabStock SET quantity = quantity - ? WHERE item_name = ?", (quantity, item_name))
            print(f"Removed {quantity} units of {item_name}.")
        else:
            print("Insufficient stock or item not found.")

    def display_all(self):
        stock = self.db.fetch_all("SELECT * FROM LabStock")
        for item in stock:
            print(f"{item[0]}: {item[1]} units")

# Hospital Class
class Hospital:
    def __init__(self):
        self.db = Database()
        self.doctor = Doctor(self.db)
        self.patient = Patient(self.db)
        self.room = Room(self.db)
        self.appointment = Appointment(self.db)
        self.medicine_stock = MedicineStock(self.db)
        self.lab_stock = LabStock(self.db)
        self.Payment=Payment(self.db)
        self.billing = Billing(self.db)

    def close(self):
        self.db.close()

# Main Program
if __name__ == "__main__":
    hospital = Hospital()

    while True:
        print('Hospital Management System')
        print("1. Add Doctor\n2. Remove Doctor\n3. Add Patient\n4. Remove Patient\n5. Add Room\n6. Remove Room")
        print("7. Assign Room\n8. Schedule Appointment\n9. Remove Appointment\n10. Buy Medicine")
        print("11. Add Medicine\n12. Remove Medicine\n13. Display Doctors\n14. Display Patients\n15. Display Rooms")
        print("16. Display Appointments\n17. Display Medicine Stock\n18. Add Lab Item\n19. Remove Lab Item")
        print("20. Display Lab Stock\n21. Add Payment\n22. Display All Payments\n23. Search Payment by Patient")
        print("24. Generate Bill\n25. Display Bill\n26. Display All Bills\n27. Exit")

        choice = input("Enter your choice: ")

        if choice == '1':
            hospital.doctor.add()
        elif choice == '2':
            hospital.doctor.remove()
        elif choice == '3':
            hospital.patient.add()
        elif choice == '4':
            hospital.patient.remove()
        elif choice == '5':
            hospital.room.add()
        elif choice == '6':
            hospital.room.remove()
        elif choice == '7':
            hospital.room.assign()
        elif choice == '8':
            hospital.appointment.schedule()
        elif choice == '9':
            hospital.appointment.remove()
        elif choice == '10':
            hospital.medicine_stock.buy()
        elif choice == '11':
            hospital.medicine_stock.add()
        elif choice == '12':
            hospital.medicine_stock.remove()
        elif choice == '13':
            hospital.doctor.display_all()
        elif choice == '14':
            hospital.patient.display_all()
        elif choice == '15':
            hospital.room.display_all()
        elif choice == '16':
            hospital.appointment.display_all()
        elif choice == '17':
            hospital.medicine_stock.display_all()
        elif choice == '18':
            hospital.lab_stock.add()
        elif choice == '19':
            hospital.lab_stock.remove()
        elif choice == '20':
            hospital.lab_stock.display_all()
        elif choice == '21':
            hospital.Payment.add_payment()
        elif choice == '22':
            hospital.Payment.display_all_payments()
        elif choice == '23':
            hospital.Payment.search_payment()
        elif choice == '24':
            hospital.billing.generate_bill()
        elif choice == '25':
            hospital.billing.display_bill()
        elif choice == '26':
            hospital.billing.display_all_bills()
        elif choice == '27':
            hospital.close()
            break
        else:
            print("Invalid choice.")
