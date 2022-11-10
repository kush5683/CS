import pymysql.cursors
import hashlib


hasher = hashlib.sha256()

reg_map = []

with open("SSN-to-port.txt", "r") as registration:
    registration = registration.readlines()
    for line in registration:
        ssn, port = line.split()
        # update can only take bytes as input so encode the ssn to ascii bytes and then update the hash object with it
        hasher.update(bytes(ssn, "ascii"))
        reg_map.append((hasher.hexdigest(),
                       0, ssn))  # append the hashed ssn, 0, to be added to the DB and the raw ssn string to be printed out to the reg_map list
    # print(reg_map)

# exit()


# Connect to the database and insert the data

for entry in reg_map[:10]:
    connection = pymysql.connect(user='netsecuser', password='SuperCoolNetSecPassword1000!!',
                                 host='71.233.252.195',
                                 database='netsec')
    with connection:
        with connection.cursor() as cursor:
            # Create a new record

            insert = f"INSERT INTO SSNs (SSN, IPAddr) VALUES ('{entry[0]}', '{entry[1]}');"
            print(entry[2])
            cursor.execute(insert)
            connection.commit()


connection = pymysql.connect(user='netsecuser', password='SuperCoolNetSecPassword1000!!',
                             host='71.233.252.195',
                             database='netsec')

# print the table
with connection.cursor() as cursor:
    select = "SELECT * FROM SSNs"
    cursor.execute(select)
    result = cursor.fetchone()
    print(result)
