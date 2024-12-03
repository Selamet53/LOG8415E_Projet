# project
mysql = '''#!/bin/bash
sudo apt-get update && sudo apt-get upgrade -y
sudo apt install -y mysql-server sysbench unzip

# Go to ~/
cd /home/ubuntu

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
EOF

chown ubuntu:ubuntu /home/ubuntu/main.py
sleep 5

cd /home/ubuntu
nohup /home/ubuntu/venv/bin/uvicorn  main:app --host 0.0.0.0 --port 8000 > /home/ubuntu/uvicorn.log 2>&1 &
'''
proxy = '''#!/bin/bash
#!/bin/bash
sudo apt-get update && sudo apt-get upgrade -y
sudo apt-get install -y python3 python3-pip python3-venv
python3 -m venv /home/ubuntu/venv

source /home/ubuntu/venv/bin/activate

pip install fastapi uvicorn

cat <<EOF > /home/ubuntu/main.py
from fastapi import FastAPI
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("Proxy")

app = FastAPI()

@app.get("/")
async def root():
    message = "Instance has received the request"
    logger.info(message)
    return {"message": message + " from Proxy"}
EOF

chown ubuntu:ubuntu /home/ubuntu/main.py
sleep 5

cd /home/ubuntu
nohup /home/ubuntu/venv/bin/uvicorn  main:app --host 0.0.0.0 --port 8000 > /home/ubuntu/uvicorn.log 2>&1 &
'''
