"""
Test02
"""

from time import time
from string import Template
import base64
import requests
import ads

# Impostazioni iniziali
BASE_URL = "https://modeldeployment.eu-frankfurt-1.oci.customer-oci.com"
ENDPOINT = f"{BASE_URL}/ocid1.datasciencemodeldeployment.oc1.eu-frankfurt-1.amaaaaaa2xxap7yay6gufqr2jv6d6rvfdxcon2mqv7lmjkmnyc6wazxvweqq/predict"


# in secs
TIMEOUT = 60


def encode_image(image_path):
    """Converte un'immagine in base64 per l'invio."""
    try:
        with open(image_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode("utf-8")
    except FileNotFoundError:
        raise Exception(f"Immage not found: {image_path}")
    except Exception as e:
        raise Exception(f"Error in processin image: {e}")


def create_payload(request, encoded_image):
    """Crea il payload JSON per la richiesta al modello."""
    return {
        "model": "odsc-llm",
        "messages": [
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": Template("""<|image_1|>\n $prompt""").substitute(
                            prompt=request
                        ),
                    },
                    {
                        "type": "image_url",
                        "image_url": {"url": f"data:image/jpeg;base64,{encoded_image}"},
                    },
                ],
            }
        ],
        "max_tokens": 1024,
        "temperature": 0.1,
        "top_p": 0.9,
    }


def send_request(endpoint, payload, auth):
    """Invia la richiesta POST all'endpoint specificato."""
    try:
        response = requests.post(endpoint, json=payload, auth=auth, timeout=TIMEOUT)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        raise Exception(f"Error in model invocation: {e}")


# Programma principale
if __name__ == "__main__":
    IMAGE_PATH = "./image2.png"
    REQUEST = """Create a detailed description of what you see in the photo.
    What do you think could be the parts to replace to repair the car? Make a bullet list"""

    # Auth
    ads.set_auth(auth="api_key", oci_config_location="~/.oci/config", profile="DEFAULT")
    auth = ads.common.auth.default_signer()["signer"]

    t_start = time()

    try:
        encoded_image = encode_image(IMAGE_PATH)
        payload = create_payload(REQUEST, encoded_image)
        response = send_request(ENDPOINT, payload, auth)

        t_elapsed = round(time() - t_start, 1)

        print("\nRequest completed in:", t_elapsed, "sec.")
        print("")
        print("Request: ", REQUEST)
        print("")
        print("Response:")
        print(response["choices"][0]["message"]["content"])
        print("")

    except Exception as e:
        print(f"Error: {e}")
