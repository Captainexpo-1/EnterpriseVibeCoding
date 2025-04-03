import requests
import json
import subprocess
import os
import sys
import argparse

SYSTEM_PROMPT = open(os.path.join(os.path.dirname(__file__), "system_prompt.txt")).read()


API_URL = "https://ai.hackclub.com"
def get_response(code: str) -> dict:
    response = requests.post(
        API_URL + "/chat/completions",
        json={
            "messages": [
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": f"{{ \"text\": \"{code}\" }}" }
            ]
        }
    )
    print("Response status code:", response.status_code)
    return response.json().get("choices", [{}])[0].get("message", {}).get("content", "")

def compile(code: str, path: str) -> None:
    print("Compiling the provided code...")
    resp = get_response(code)
    try:
        resp
    except json.JSONDecodeError:
        # Handle the case where the response is not valid JSON
        print(resp)
        raise Exception("Failed to decode JSON from the compiler API. Response: {}".format(resp))
    print("Received response from the compiler API")
    #e = resp.get("errors", [])
    #if len(e) > 0:
    #    raise Exception('\n'.join([str(i) for i in e]))

    with open(path, "w") as f:
        # Write the C code to the file
        f.write(resp)
    
    

def main():
    parser = argparse.ArgumentParser(description="Compile and run C code.")
    parser.add_argument("code", type=str, help="The C code to compile and run.")
    parser.add_argument("--path", type=str, default="temp.py", help="The path to the output file.")
    args = parser.parse_args()

    code = open(args.code).read()
    path = args.path
    
    compile(code, path)

    with open(path, "r") as f:
        code = f.read()
    
    exec(code)

if __name__ == "__main__":
    main()
