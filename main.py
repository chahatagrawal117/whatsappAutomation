
import logging, os, sys
import datetime
import time

import pywhatkit
import csv
from utils import TEXT_FILE_PATH, IMAGE_FILE_PATH, DATA_FILE_PATH, DEMO_FILE_PATH
logging.basicConfig(level=logging.INFO)

def change_phone_number_to_indian(phone_number):
    phone_number = str(phone_number)
    phone_number = phone_number.strip()
    if len(phone_number) != 10:
        return None
    phone_number = "+91"+phone_number
    return phone_number
def find_current_time():
    # Get current timestamp
    current_time = datetime.datetime.now()

    # Extract hour and minute
    current_hour = current_time.hour
    current_minute = current_time.minute
    return current_hour, current_minute

def read_content_from_file(file_path):
    try:
        filename = file_path
        full_text = ""

        # Open the file in read mode
        with open(filename, "r") as file:
            # Read each line from the file and concatenate it to the full_text variable
            for line in file:
                full_text += line
        logging.info("sending this message....")
        logging.info(full_text)
        return full_text
    except Exception as e:
        logging.error("Not able to open file ")


def send_message(phone_number, msg, image_path):
    try:
        current_hour, current_minute = find_current_time()
        logging.info("Current_time-{}:{}".format(current_hour, current_minute))
        if image_path == "":
            pywhatkit.sendwhatmsg(phone_no=phone_number, message=msg, time_hour=current_hour,
                                  time_min=current_minute + 1,
                                  tab_close=True, wait_time=30)
            # time.sleep(5)
        else:
            pywhatkit.sendwhats_image(receiver=phone_number, img_path=IMAGE_FILE_PATH, caption=msg, tab_close=True,
                                      wait_time=30)

        return True

    except Exception as e:
        logging.error("Exception {}".format(e))
        return None

def get_list_of_phone_numbers_from_csv(file_path):
    try:
        phone_list = []
        with open(file_path, mode='r') as file:
            # Create a CSV reader object using DictReader
            csv_reader = csv.DictReader(file)

            # Iterate over each row in the CSV file
            for row in csv_reader:
                # Print each row as a dictionary
                phone_list.append(row)
        return phone_list
    except Exception as e:
        logging.error("Error in getting phone list: e: {}".format(e))
        return None


def main():
    # commands used
    # python main.py demo  -> it will run demo data file without image
    # python main.py data  -> it will run main data file without image
    # python main.py demo image -> it will run demo data file with image
    # python main.py data image -> it will run main data file with image

    file_path_name = sys.argv[1]  # demo or data
    image_path = ""
    if len(sys.argv)==3 and sys.argv[2]=="image":
        image_path = IMAGE_FILE_PATH

    csv_file_path = DATA_FILE_PATH
    if file_path_name == "demo":
        csv_file_path = DEMO_FILE_PATH

    phone_numbers_list = get_list_of_phone_numbers_from_csv(csv_file_path)
    msg = read_content_from_file(TEXT_FILE_PATH)

    for phone in phone_numbers_list:
        phone_number = phone["PhoneNumber"]
        indian_phone_number = change_phone_number_to_indian(phone_number)
        if indian_phone_number is None:
            logging.info("This phone number is not valid, please check {}".format(phone_number))
            continue
        for i in range(0,5):
            logging.info("Sending msg to phone no. {}".format(indian_phone_number))
            status = send_message(phone_number=indian_phone_number, msg=msg, image_path=image_path)
            if status is None:
                logging.info("Trying again on this no. {}".format(indian_phone_number))
                time.sleep(5)
            else:
                break


main()