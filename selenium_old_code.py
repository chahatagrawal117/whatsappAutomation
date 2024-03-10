import pyautogui as pg
import webbrowser as web
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import csv

from mysql.connector import (connection)

time_delay = 14


def getDatabaseConnection():
    cnx = connection.MySQLConnection(user='root', password='Home@1234', host='192.168.1.5', database='movedb');
    return cnx;


def getPendingMessageFromDB():
    cnx = getDatabaseConnection();
    query = ("SELECT * from emailsdetails where whtsup_status < 1 ");
    # query = ("SELECT * from emailsdetails");
    dataFrame = pd.DataFrame(pd.read_sql_query(query, cnx));
    print(dataFrame.shape);
    cnx.close();
    return dataFrame;


def getJobDetailsFromProcessedIdandClientId(processedId, clientId):
    cnx = getDatabaseConnection();
    query = "SELECT * From ( ( ProcessingDetails Inner Join MyOrderDetails on ProcessingDetails.processingID=MyOrderDetails.jobProcessingID)" \
            " Inner join MyOrder on MyOrder.oId=MyOrderDetails.oId ) " \
            + " Inner Join clients on clients.client_id=Myorder.oclientId" \
            + " where clients.client_id=" + f'{clientId}' \
            + " and ProcessingDetails.processingID=" + f'{processedId}';

    dataFrame = pd.DataFrame(pd.read_sql_query(query, cnx));
    print(dataFrame.shape);
    cnx.close();
    return dataFrame;


def getJobDetailsFromOrderIdandClientId(orderId):
    cnx = getDatabaseConnection();
    cursor = cnx.cursor();
    # query = "SELECT * FROM MyOrderDetails where MyOrderDetails.oId=" + f'{orderId}';
    query = "SELECT * FROM ( MyOrderDetails Inner Join MyOrder on MyOrder.oId=MyOrderDetails.oId) " \
            " Inner Join clients on clients.client_id=Myorder.oclientId" \
            + " where MyOrderDetails.oId=" + f'{orderId}';
    dataFrame = pd.DataFrame(pd.read_sql_query(query, cnx));
    print(dataFrame.shape);
    cursor.close()
    cnx.close();
    return dataFrame;


def getWhatsMessageBodyForProcessedOrder(dataframe):
    if len(dataframe) == 0:
        return -1, -1
    jobDetails = "Dear Client %0a*Your order has been processed.* %0aYour Processed Order Details are as follows:-%0a";
    eod = "";
    mobileNo = "";
    # print('hello chahat i am hereee')
    for index, row in dataframe.iterrows():
        jobDetails = jobDetails \
                     + "Job Details :: " + row['jobDetails'] + "%0a" \
                     + "Job Type :: " + row['pName'] + "%0a" \
                     + "Job Qty :: " + str(row['Qty']) + "%0a"
        eod = row['pExpDelDate'];
        mobileNo = row['client_mobile'];

    eod = eod.strftime("%d-%b-%Y")
    jobDetails = jobDetails + "%0a %0a" \
                 + "*Expected Date of delivery:: " + str(eod) + "*"
    mobile = f'91_{mobileNo}'
    message = jobDetails;
    return mobile, message;


def getWhatsMessageBodyForReadyOrder(dataframe):
    if len(dataframe) == 0:
        return -1, -1
    jobDetails = "Dear Client %0a*Your order is ready for delivery.* %0aReady Order Details are as follows:-%0a";
    mobileNo = "";
    for index, row in dataframe.iterrows():
        jobDetails = jobDetails \
                     + "Job Details :: " + row['jobDetails'] + "%0a" \
                     + "Job Type :: " + row['pName'] + "%0a" \
                     + "Job Qty :: " + str(row['Qty']) + "%0a"
        mobileNo = row['client_mobile'];

    mobile = f'91_{mobileNo}'
    message = jobDetails;
    return mobile, message;


def getWhatsMessageBodyForReceivedOrder(dataframe):
    if len(dataframe) == 0:
        return -1, -1
    jobDetails = "Dear Client %0a*Your order has been received.* %0aOrder Details are as follows:- %0a";
    mobileNo = "";
    for index, row in dataframe.iterrows():
        jobDetails = jobDetails + "Job Details :: " + row['jobDetails'] + "%0a" + "Job Type :: " + row[
            'pName'] + "%0a" + "Job Qty :: " + str(row['Qty']) + "%0a"
        mobileNo = row['client_mobile'];

    mobile = f'91_{mobileNo}'
    message = jobDetails
    return mobile, message;


def updateWhtsMessageStatus(eId, wStatus):
    conn = getDatabaseConnection()
    cursor = conn.cursor()
    qry = "UPDATE EmailsDetails SET " \
          + " whtsup_status= " + f'{wStatus}' + " where eId= " + f'{eId}'
    print(qry)
    cursor.execute(qry)
    conn.commit()
    return 1


def is_trying_to_reach_phone():
    try:
        driver.find_element(By.XPATH, "//*[text()='Trying to reach phone']")
        return True
    except:
        try:
            driver.find_element(By.XPATH, "//*[text()='Phone not connected']")
            return True
        except:
            return False


def is_mobile_number_invalid():
    try:
        driver.find_element(By.XPATH, "//*[text()='Phone number shared via url is invalid.']")
        return True;
    except:
        return False


def send_message(number, message, count):
    if count >= 5:
        with open('logs.csv', 'a') as log_file:
            csv_writer = csv.writer(log_file)
            csv_writer.writerow([number, time.strftime('%I:%M %p on %b %d, %Y'), message])
        return -1

    time.sleep(5)
    driver.get("https://web.whatsapp.com/send?phone=" + number + "&text=" + message)
    wait = WebDriverWait(driver, 180)  # max timeout period
    try:

        element = wait.until(
            EC.element_to_be_clickable(
                (By.XPATH, "//*[@id='main']/footer/div[1]/div/span[2]/div/div[2]/div[2]/button/span")))
        element.click()  # message sent successfully
    except:
        print(f'Error is coming in sending message to {number} and now trying again')
        network_error_time = 0
        while is_trying_to_reach_phone() and network_error_time < 45:
            network_error_time += 1
            print('Please connect to Rajesh Agrawal phone ASAP - Network Error')
            time.sleep(120)
        if is_trying_to_reach_phone():
            return send_message(number, message, count)

        if is_mobile_number_invalid():
            print('Given Mobile number is invalid')
            with open('invalid_numbers_sheet.csv', 'a') as log_file:
                csv_writer = csv.writer(log_file)
                csv_writer.writerow([number, time.strftime('%I:%M %p on %b %d, %Y'), message])
            return 1
        return send_message(number, message, count + 1)

    time.sleep(5)
    return 1


#  Main program to execute here


def do_task():
    dataframe = getPendingMessageFromDB();
    # print(dataframe)
    loop = 0
    for index, row in dataframe.iterrows():
        eId = row['eID'];
        refType = row['ReferenceType'];
        refId = row['ReferenceId'];
        clientId = row['receipientClientId'];
        refType = row['ReferenceType'];
        if (refType == 5):
            dataFrame = getJobDetailsFromProcessedIdandClientId(refId, clientId);
            print(dataFrame)
            mobile, message = getWhatsMessageBodyForProcessedOrder(dataFrame);
        elif (refType == 1):
            dataFrame = getJobDetailsFromOrderIdandClientId(refId);
            mobile, message = getWhatsMessageBodyForReceivedOrder(dataFrame);
        elif (refType == 10):
            dataFrame = getJobDetailsFromProcessedIdandClientId(refId, clientId);
            mobile, message = getWhatsMessageBodyForReadyOrder(dataFrame);
        print("Sending Msg to  ::", mobile);
        if mobile != -1:
            status = send_message(mobile, message, 1);
        else:
            status = 1
        updateWhtsMessageStatus(eId, status);


options = webdriver.ChromeOptions()
options.add_argument("user-data-dir=C:\\Users\\shree\\Desktop\\whatsappAutomation\\chrome-data")
driver = webdriver.Chrome(options=options,
                          executable_path="C:\\Users\\shree\\Desktop\\whatsappAutomation\\chromedriver")
print("Starting program")
while 1:
    print('sending whatsapp messages.......')
    do_task()
    print('completed whatsapp messages.. waiting for more')
    time.sleep(120)