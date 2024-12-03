import asyncio
import aiohttp

async def call_endpoint_http(session, i):
    url = "http://54.174.154.21:8000/"
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

async def main():
    num_requests = 5
    print(f"Sending {num_requests} requests to /")

    async with aiohttp.ClientSession() as session:
        tasks = [call_endpoint_http(session, i) for i in range(num_requests)]
        await asyncio.gather(*tasks)

if __name__ == "__main__":
    asyncio.run(main())
