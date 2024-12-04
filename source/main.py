import asyncio
import aiohttp

# For testing
async def call_endpoint_http(session, i):
    url = "http://3.82.44.159:8000/" # replace the ip with the gatekeeper ip
    headers = {'content-type': 'application/json'}
    try:
        print(f"Sending request {i} to {url}")
        async with session.get(url, headers=headers) as response:
            status_code = response.status
            response_json = await response.json()
            print(f"Response: {status_code}, {response_json}")
            return status_code, response_json
    except Exception as e:
        return None, str(e)
    
# Read data from a table. Exemple: actor
async def read_data(session, i):
    url = f"http://3.82.44.159:8000/read/actor" # replace the ip with the gatekeeper ip
    headers = {'content-type': 'application/json'}
    try:
        print(f"Sending read request {i} to {url}")
        async with session.get(url, headers=headers) as response:
            status_code = response.status
            response_json = await response.json()
            print(f"Read Response: {status_code}, {response_json}")
            return status_code, response_json
    except Exception as e:
        return None, str(e)

# Write data to a table. TODO: Finish the implementation because of errors from manager
async def write_data(session, i):
    url = f"http://54.198.231.67:8000/write" # replace the ip with the gatekeeper ip
    headers = {'content-type': 'application/json'}
    payload = {
        "table": "table_name",
        "column": "column_name",
        "value": f"value_{i}"
    }
    try:
        print(f"Sending write request {i} to {url}")
        async with session.post(url, headers=headers, json=payload) as response:
            status_code = response.status
            response_json = await response.json()
            print(f"Write Response: {status_code}, {response_json}")
            return status_code, response_json
    except Exception as e:
        return None, str(e)

async def main():
    num_requests = 1000
    print(f"Sending {num_requests} requests to /")

    async with aiohttp.ClientSession() as session:
        # tasks = [call_endpoint_http(session, i) for i in range(num_requests)]
        # await asyncio.gather(*tasks)

        read_tasks = [read_data(session, i) for i in range(num_requests)]
        await asyncio.gather(*read_tasks)

        write_tasks = [write_data(session, i) for i in range(num_requests)]
        await asyncio.gather(*write_tasks)

if __name__ == "__main__":
    asyncio.run(main())
