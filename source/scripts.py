# project: the fast api code is mostly from the first lab assignment but modified for this project's needs.
manager = '''#!/bin/bash
sudo apt-get update && sudo apt-get upgrade -y
sudo apt install -y mysql-server sysbench unzip python3 python3-pip python3-venv

# Setup MySQL
MYSQL_PASSWORD="root"
sudo mysql -e "ALTER USER 'root'@'localhost' IDENTIFIED WITH 'mysql_native_password' BY '$MYSQL_PASSWORD';"

# Setup sakila db
wget https://downloads.mysql.com/docs/sakila-db.zip
unzip sakila-db.zip

mysql -u root -p"$MYSQL_PASSWORD" -e "SOURCE ./sakila-db/sakila-schema.sql ; SOURCE ./sakila-db/sakila-data.sql ;"

# Running sysbench
sudo sysbench /usr/share/sysbench/oltp_read_only.lua --mysql-db=sakila --mysql-user="root" --mysql-password="$MYSQL_PASSWORD" prepare
sudo sysbench /usr/share/sysbench/oltp_read_only.lua --mysql-db=sakila --mysql-user="root" --mysql-password="$MYSQL_PASSWORD" run

# MySQL Node code
# Setup python environment
python3 -m venv /home/ubuntu/venv
source /home/ubuntu/venv/bin/activate

# Install required packages
pip install fastapi uvicorn mysql-connector-python

cat <<EOF > /home/ubuntu/main.py
from fastapi import FastAPI, HTTPException
import mysql.connector
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("Cluster")

app = FastAPI()

# MySQL connection config
db_config = {
    "user": "root",
    "password": "root",
    "host": "127.0.0.1",
    "database": "sakila",
}

@app.get("/")
async def root():
    message = "Instance has received the request"
    logger.info(message)
    return {"message": message + " from Manager Node!"}

@app.get("/read/{table}")
async def read_data(table: str):
    try:
        connection = mysql.connector.connect(**db_config)
        cursor = connection.cursor(dictionary=True)
        cursor.execute(f"SELECT * FROM {table} LIMIT 10;")
        results = cursor.fetchall()
        cursor.close()
        connection.close()
        return {"data": results}
    except mysql.connector.Error as err:
        logger.error(f"Error: {err}")
        raise HTTPException(status_code=500, detail="Failed to read data")

@app.post("/write") # TODO errors
async def write_data(table: str, column: str, value: str):
    try:
        connection = mysql.connector.connect(**db_config)
        cursor = connection.cursor()
        cursor.execute(f"INSERT INTO {table} ({column}) VALUES (%s);", (value,))
        connection.commit()
        cursor.close()
        connection.close()
        logger.info(f"Inserted {value} into {table}({column})")
        return {"message": f"Inserted {value} into {table}({column})"}
    except mysql.connector.Error as err:
        logger.error(f"Error: {err}")
        raise HTTPException(status_code=500, detail="Failed to write data")
EOF

# Change ownership and permissions
chown ubuntu:ubuntu /home/ubuntu/main.py
sleep 5

# Run FastAPI app
cd /home/ubuntu
nohup /home/ubuntu/venv/bin/uvicorn main:app --host 0.0.0.0 --port 8000 > /home/ubuntu/uvicorn.log 2>&1 &
'''
worker = '''#!/bin/bash
sudo apt-get update && sudo apt-get upgrade -y
sudo apt install -y mysql-server sysbench unzip python3 python3-pip python3-venv

# Setup MySQL
MYSQL_PASSWORD="root"
sudo mysql -e "ALTER USER 'root'@'localhost' IDENTIFIED WITH 'mysql_native_password' BY '$MYSQL_PASSWORD';"

# Setup sakila db
wget https://downloads.mysql.com/docs/sakila-db.zip
unzip sakila-db.zip

mysql -u root -p"$MYSQL_PASSWORD" -e "SOURCE ./sakila-db/sakila-schema.sql ; SOURCE ./sakila-db/sakila-data.sql ;"

# Running sysbench
sudo sysbench /usr/share/sysbench/oltp_read_only.lua --mysql-db=sakila --mysql-user="root" --mysql-password="$MYSQL_PASSWORD" prepare
sudo sysbench /usr/share/sysbench/oltp_read_only.lua --mysql-db=sakila --mysql-user="root" --mysql-password="$MYSQL_PASSWORD" run

# MySQL Node code
# Setup python environment
python3 -m venv /home/ubuntu/venv
source /home/ubuntu/venv/bin/activate

# Install required packages
pip install fastapi uvicorn mysql-connector-python

cat <<EOF > /home/ubuntu/main.py
from fastapi import FastAPI, HTTPException
import mysql.connector
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("Cluster")

app = FastAPI()

# MySQL connection config
db_config = {
    "user": "root",
    "password": "root",
    "host": "127.0.0.1",
    "database": "sakila",
}

@app.get("/")
async def root():
    message = "Instance has received the request"
    logger.info(message)
    return {"message": message + " from Worker Node!"}

@app.get("/read/{table}")
async def read_data(table: str):
    try:
        connection = mysql.connector.connect(**db_config)
        cursor = connection.cursor(dictionary=True)
        cursor.execute(f"SELECT * FROM {table} LIMIT 10;")
        results = cursor.fetchall()
        cursor.close()
        connection.close()
        return {"data": results}
    except mysql.connector.Error as err:
        logger.error(f"Error: {err}")
        raise HTTPException(status_code=500, detail="Failed to read data")
EOF

# Change ownership and permissions
chown ubuntu:ubuntu /home/ubuntu/main.py
sleep 5

# Run FastAPI app
cd /home/ubuntu
nohup /home/ubuntu/venv/bin/uvicorn main:app --host 0.0.0.0 --port 8000 > /home/ubuntu/uvicorn.log 2>&1 &
'''
gatekeeper = '''#!/bin/bash
sudo apt-get update && sudo apt-get upgrade -y
sudo apt-get install -y python3 python3-pip python3-venv
python3 -m venv /home/ubuntu/venv

source /home/ubuntu/venv/bin/activate

pip install fastapi uvicorn requests

# Gatekeeper application
cat <<EOF > /home/ubuntu/main.py
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import RedirectResponse
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("Gatekeeper")

app = FastAPI()

@app.get("/")
async def root():
    print("Forwarding request to Trusted Host: TRUSTED_HOST_URL")
    target_url = f"http://TRUSTED_HOST_URL:8000"
    
    return RedirectResponse(url=target_url)

@app.get("/read/{table}")
async def read_data(table: str):
    try:
        print("Forwarding Read request to Trusted Host: TRUSTED_HOST_URL")
        target_url = f"http://TRUSTED_HOST_URL:8000"
        return RedirectResponse(url=target_url)
    except mysql.connector.Error as err:
        logger.error(f"Error: {err}")
        raise HTTPException(status_code=500, detail="Failed to read data")

@app.post("/write")
async def write_data(table: str, column: str, value: str):
    try:
        print("Forwarding Write request to Trusted Host: TRUSTED_HOST_URL")
        target_url = f"http://TRUSTED_HOST_URL:8000"
        return RedirectResponse(url=target_url)
    except mysql.connector.Error as err:
        logger.error(f"Error: {err}")
        raise HTTPException(status_code=500, detail="Failed to write data")
EOF

chown ubuntu:ubuntu /home/ubuntu/main.py
sleep 5

cd /home/ubuntu
nohup /home/ubuntu/venv/bin/uvicorn  main:app --host 0.0.0.0 --port 8000 > /home/ubuntu/uvicorn.log 2>&1 &
'''
trusted_host ='''#!/bin/bash
sudo apt-get update && sudo apt-get upgrade -y
sudo apt-get install -y python3 python3-pip python3-venv
python3 -m venv /home/ubuntu/venv

source /home/ubuntu/venv/bin/activate

pip install fastapi uvicorn requests

# Gatekeeper application
cat <<EOF > /home/ubuntu/main.py
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import RedirectResponse
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("TrustedHost")

app = FastAPI()

@app.get("/")
async def root():
    print("Forwarding request to the proxy: PROXY_URL")
    target_url = f"http://PROXY_URL:8000"
    return RedirectResponse(url=target_url)

@app.get("/read/{table}")
async def read_data(table: str):
    try:
        print("Forwarding Read request to the proxy: PROXY_URL")
        target_url = f"http://PROXY_URL:8000"
        return RedirectResponse(url=target_url)
    except mysql.connector.Error as err:
        logger.error(f"Error: {err}")
        raise HTTPException(status_code=500, detail="Failed to read data")

@app.post("/write")
async def write_data(table: str, column: str, value: str):
    try:
        print("Forwarding Write request to Trusted Host: PROXY_URL")
        target_url = f"http://PROXY_URL:8000"
        return RedirectResponse(url=target_url)
    except mysql.connector.Error as err:
        logger.error(f"Error: {err}")
        raise HTTPException(status_code=500, detail="Failed to write data")
EOF

chown ubuntu:ubuntu /home/ubuntu/main.py
sleep 5

cd /home/ubuntu
nohup /home/ubuntu/venv/bin/uvicorn  main:app --host 0.0.0.0 --port 8000 > /home/ubuntu/uvicorn.log 2>&1 &
'''
proxy = '''#!/bin/bash
sudo apt-get update && sudo apt-get upgrade -y
sudo apt-get install -y python3 python3-pip python3-venv
python3 -m venv /home/ubuntu/venv

source /home/ubuntu/venv/bin/activate

pip install fastapi uvicorn requests

# Gatekeeper application
cat <<EOF > /home/ubuntu/main.py
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import RedirectResponse
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("Proxy")

app = FastAPI()

@app.get("/")
async def root():
    print("Forwarding request to the proxy: MANAGER_URL")
    target_url = f"http://MANAGER_URL:8000"
    
    return RedirectResponse(url=target_url)

@app.get("/read/{table}")
async def read_data(table: str):
    try:
        print("Forwarding Read request to the proxy: WORKER1_URL")
        target_url = f"http://WORKER1_URL:8000"
        return RedirectResponse(url=target_url)
    except mysql.connector.Error as err:
        logger.error(f"Error: {err}")
        raise HTTPException(status_code=500, detail="Failed to read data")

@app.post("/write")
async def write_data(table: str, column: str, value: str):
    try:
        print("Forwarding Write request to Trusted Host: MANAGER_URL")
        target_url = f"http://MANAGER_URL:8000"
        return RedirectResponse(url=target_url)
    except mysql.connector.Error as err:
        logger.error(f"Error: {err}")
        raise HTTPException(status_code=500, detail="Failed to write data")
EOF

chown ubuntu:ubuntu /home/ubuntu/main.py
sleep 5

cd /home/ubuntu
nohup /home/ubuntu/venv/bin/uvicorn  main:app --host 0.0.0.0 --port 8000 > /home/ubuntu/uvicorn.log 2>&1 &
'''
