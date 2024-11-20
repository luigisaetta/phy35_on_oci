import requests
from time import time
from string import Template
import base64
import ads

endpoint = "https://modeldeployment.eu-frankfurt-1.oci.customer-oci.com/ocid1.datasciencemodeldeployment.oc1.eu-frankfurt-1.amaaaaaa2xxap7yay6gufqr2jv6d6rvfdxcon2mqv7lmjkmnyc6wazxvweqq/predict"

image_path = "/Users/lsaetta/Progetti/test_phy3/image2.png"


# Set Resource principal. For other signers, please check `oracle-ads` documentation
ads.set_auth(auth="api_key", oci_config_location="~/.oci/config", profile="DEFAULT")

auth = ads.common.auth.default_signer()["signer"]


def encode_image(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode("utf-8")


header = {"Content-Type": "application/json"}

REQUEST = "Create a detailed description of what you see in the photo. What do you think could be the parts to replace to repair the car?"

payload = {
    "model": "odsc-llm",
    "messages": [
        {
            "role": "user",
            "content": [
                {
                    "type": "text",
                    "text": Template("""<|image_1|>\n $prompt""").substitute(
                        prompt=REQUEST
                    ),
                },
                {
                    "type": "image_url",
                    "image_url": {
                        "url": f"data:image/jpeg;base64,{encode_image(image_path)}"
                    },
                },
            ],
        }
    ],
    "max_tokens": 1024,
    "temperature": 0.1,
    "top_p": 0.9,
}

t_start = time()

REQUEST = "Create a detailed description of what you see in the photo."

response = requests.post(endpoint, json=payload, auth=auth, headers={}).json()

t_elapsed = round(time() - t_start, 1)

print()
print("The request:")
print(REQUEST)
print("The response:")
print(response["choices"][0]["message"]["content"])
print()
print("Elapsed time:", t_elapsed, "sec.")
