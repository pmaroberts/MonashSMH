import requests
import os


# function for uploading a file to octoprint, takes the file path and the printer number as an input and uploads it locally to the pi
# Importantly the printer numbers are 1 and 2 NOT 0 and 1
def upload_file_to_octoprint(filePath, printerNumber) -> bool:
    api_url_printer1 = "http://172.31.1.225:5000/api/files/local"
    api_url_printer2 = "http://172.31.1.226:5000/api/files/local"

    # Set the API endpoint URL
    if printerNumber == 1:
        api_url = api_url_printer1
        # Set the headers
        headers = {
            "X-Api-Key": "FC41141214E346D89754615FD91CF5EE",
        }
    elif printerNumber == 2:
        api_url = api_url_printer2
        # Set the headers
        headers = {
            "X-Api-Key": "3098EB294377487C83723A0358AC9A6F",
        }
    else:
        print("Invalid printer number.")
        return False

    fileName = os.path.basename(filePath)

    # Set the payload as multipart/form-data
    payload = {
        "file": (fileName, open(filePath, "rb"), "application/octet-stream"),
        "select": "true",
        "print": "true",
    }

    try:
        # Send the POST request
        response = requests.post(api_url, headers=headers, files=payload)

        # Check the response status
        if response.status_code == 201:
            print("File uploaded successfully.")
            print("Location:", response.headers["Location"])
            print("Upload Response:", response.text)
            return True
        else:
            print(f"File upload failed. Status code: {response.status_code}")
            print("Error Response:", response.text)
            return False
    except FileNotFoundError:
        print("File not found.")
        return False


# # Test Usage
# filePath = "C:/Users/jacob/OneDrive/Documents/1UNI/2023Sem1/ENG4701/Letters of Alphbet/D.gcode"
# upload_file_to_octoprint(filePath, 2)
