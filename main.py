import requests
import json
import subprocess

SYSTEM_PROMPT = """
You are acting as a compiler for a new, innovative esolang. I will provide a JSON object in this form:
{ "text": str }

You will then respond with the equivalent python program as plain text without "```python ```"

If you find errors in the provided code, prefix the response with <<ERROR>> and provide the errors. If there are errors, do not provide any compiled code.

DO NOT SAY ANYTHING ELSE BESIDES THE JSON RESPONSE. ALWAYS PROVIDE A RESPONSE NO MATTER WHAT

HERE IS THE SPECIFICATION FOR THE LANGUAGE:

*IN ORDER TO USE THE APPROX_EQUAL FUNCTION, YOU MUST CALL `approx_equal(a, b)` IN THE CODE. THIS FUNCTION WILL BE INJECTED INTO THE FILE. IT WILL TAKE TWO VALUES OF ANY TYPE AND RETURN A BOOLEAN INDICATING IF THEY ARE APPROXIMATELY EQUAL. IT WILL USE THE AI API TO DETERMINE THIS.*

---

# **VibeLang**  
> _Structured. Sensible. Slightly slippery._

---

## 🧠 Design Philosophy

VibeLang is a compiled, statically typed language designed to feel *close enough* to familiar C-style languages, but introduces just enough ambiguity and softness to keep you guessing. It avoids jokey keywords, but twists conventional rules in ways that are valid—but confusing.

---

## 🔤 Syntax

### ✅ Semicolons Optional

Semicolons are **optional** at line ends if:
- The next line is indented further
- Or, the current line ends with an operator, open paren, or comma

```vibe
let total = 42
let x = 10 + 
    5
```

---

### ✅ Type Inference with Weak Hints

All variables must be declared, but types are inferred unless explicitly disambiguated with a type suffix.

```vibe
let counter = 0          // inferred as int
let name = "alex"        // inferred as string
let probability:float = 0.75
```

You can override with weak annotations:

```vibe
let result: maybe int = fetchValue()
```

---

### ✅ Function Definitions

Functions are declared with `func`. Return types are inferred unless specified.

```vibe
func average(a, b) {
    return (a + b) / 2
}

func greet(name: string): string {
    return "hi, " + name
}
```

Default values can be omitted or left as `_`, which implicitly makes them nullable.

```vibe
func connect(port = 8080, host = _) {
    // host is optional but must be checked
}
```

---

### ✅ Conditional Logic

Conditionals use standard `if`, `else`, `while`, etc., but tolerate fuzzy expressions via soft equality `?=`.

```vibe
if userCount ?= "about 10" {
    log("close enough")
}

while temperature <? 100 {
    coolDown()
}
```

Soft operators:
- `?=`: approximately equal
- `<?`, `>?`: soft comparisons (may include fuzzy tolerance)
- `=~`: value pattern match (not regex, just "fuzzy match")

---

### ✅ Switch Statements Replaced with `select`

Pattern-matching-ish switch with loose case matching.

```vibe
select status {
    case 200:
        handleOK()
    case 404, 403:
        handleClientError()
    case ~500:
        handleServerError()
    default:
        retry()
}
```

`~500` matches any value "around" 500.

---

## 📐 Scoping and Blocks

Blocks are defined by indentation **or** braces—you must pick one per file.

```vibe
if ready
    beginTask()
    log("started")

// or

if ready {
    beginTask()
    log("started")
}
```

---

## 🔃 Loops

`loop` is the generic looping keyword, with context-based evaluation.

```vibe
loop while count < 10 {
    count += 1
}

loop 5 {
    retry()
}
```

Or even:

```vibe
loop until finished
    tick()
```

---

## 📦 Types

- `int`, `float`, `bool`, `string`, `char`
- `any` – like `Object`, but unsafe
- `maybe T` – nullable / optional type

---

## 🧪 Example Program

```vibe
func main() {
    let tries = 0
    let result: maybe string

    loop until result ?= "success" {
        result = tryThing()
        tries += 1
    }

    if tries <? 5 {
        log("reasonable effort")
    } else {
        warn("needed convincing")
    }
}
```

"""

APPROX_EQUAL_INJECTION = """

from typing import Any
import requests
API_URL = "https://ai.hackclub.com"
def approx_equal(a: Any, b: Any, tolerance: float = 0.01) -> bool:
    response = requests.post(
        API_URL + "/chat/completions",
        json={
            "messages": [
                {"role": "system", "content": "DETERMINE IF A and B ARE APPROXIMATELY EQUAL GIVEN SOME TOLERANCE. USE ANY METHOD YOU WANT. RETURN THE RESULT AS 'true' OR 'false' DO NOT SAY ANYTHIN BESIDES 'true' OR 'false'"},
                {"role": "user", "content": f"{{ \\"a\\": \\"{a}\\", \\"b\\": \\"{b}\\" }}" }
            ]
        }
    )
    print("Response status code:", response.status_code)
    return response.json().get("choices", [{}])[0].get("message", {}).get("content", "true") == "true"

"""

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
        f.write(APPROX_EQUAL_INJECTION + "\n" + resp)
    
    

def main():
    compile("""

func sqrt(x: float): float {
    if x <? 0 {
        warn("sqrt of negative not supported")
        return 0
    }

    let guess = x / 2
    let tolerance = 0.00001
    let current = guess
    let next = (current + x / current) / 2

    loop while abs(current - next) > tolerance {
        current = next
        next = (current + x / current) / 2
    }

    return next
}

""", "temp/test.py")
    
if __name__ == "__main__":
    main()
