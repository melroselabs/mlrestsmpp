#!/usr/bin/env python3

# mlrestsmpp -- Melrose Labs REST-SMPP 
# Copyright (c) 2021 Mark Hay / Melrose Labs Ltd

# Melrose Labs 
# melroselabs.com

import json
import logging
import traceback
from collections import defaultdict
import hashlib
import sys
import socket
import time
import threading
import collections

# https://github.com/python-smpplib/python-smpplib

import smpplib.gsm
import smpplib.client
import smpplib.consts

#

logger=logging.getLogger()
logger.setLevel(logging.INFO)

def log_err(errmsg_user,errmsg):
    print(errmsg)
    logger.error(errmsg)
    return {
        'statusCode': 500,
        'body': json.dumps({'error' :errmsg_user})
    }

messageIDdict = {}
resultCount = 0
result_available = threading.Event()

def ml_error_handler(pdu,**kwargs):
    global resultCount
    #

def submitsmresp_handler(pdu,**kwargs):
    global resultCount
    global result_available

    sys.stdout.write('sent {} {}\n'.format(pdu.sequence, pdu.message_id))
    if pdu.message_id is not None:
        messageIDdict[pdu.sequence] = str(pdu.message_id,"utf-8")
    else:
        messageIDdict[pdu.sequence] = ''
    resultCount += 1
    result_available.set()

def lambda_handler(event, context):

    body_str = event['body']
    if event['isBase64Encoded']:
        body_str = base64.b64decode(body_str)
    body = json.loads(body_str)
    
    sourceIp = event['requestContext']['identity']['sourceIp']
    transactionID = event['requestContext']['requestId']

    # check for required parameters

    if 'destinations' not in body:
        return log_err ("Missing destinations field","ERROR: Missing destinations field\n")

    if len(body['destinations'])==0:
        return log_err ("Empty destinations field","ERROR: Empty destinations field\n")
    
    maxDestinations = 100
    if len(body['destinations'])>maxDestinations:
        return log_err ("Number of destinations exceeds limit (max {} destinations)".format(maxDestinations),"ERROR: Number of destinations is greater than limit ({})\n".format(maxDestinations))
    
    # set default values for all parameters and extract parameters
    
    request = defaultdict(dict)

    request['smpp_account_config'] = defaultdict(dict)

    request['smpp_account_config']['host']=""
    if 'host' in body['smpp_account_config']:
        request['smpp_account_config']['host']=body['smpp_account_config']['host']
        
    request['smpp_account_config']['port']=2775
    if 'port' in body['smpp_account_config']:
        request['smpp_account_config']['port']=body['smpp_account_config']['port']
        
    #request['smpp_account_config']['use_tls']=False
    #if 'use_tls' in body['smpp_account_config']:
    #    request['smpp_account_config']['use_tls']=body['smpp_account_config']['use_tls']
        
    #request['smpp_account_config']['smpp_version']=3.4
    #if 'smpp_version' in body['smpp_account_config']:
    #    request['smpp_account_config']['smpp_version']=body['smpp_account_config']['smpp_version']
        
    #request['smpp_account_config']['default_data_coding']="GSM"
    #if 'default_data_coding' in body['smpp_account_config']:
    #    request['smpp_account_config']['default_data_coding']=body['smpp_account_config']['default_data_coding']
        
    request['smpp_account_config']['system_id']=""
    if 'system_id' in body['smpp_account_config']:
        request['smpp_account_config']['system_id']=body['smpp_account_config']['system_id']
        
    request['smpp_account_config']['password']=""
    if 'password' in body['smpp_account_config']:
        request['smpp_account_config']['password']=body['smpp_account_config']['password']
        
    request['smpp_account_config']['system_type']=""
    if 'system_type' in body['smpp_account_config']:
        request['smpp_account_config']['system_type']=body['smpp_account_config']['system_type']

    #request['submit_options'] = defaultdict(dict)

    #request['submit_options']['windowSizeSubmitSM']=10
    #if 'windowSizeSubmitSM' in body['submit_options']:
    #    request['submit_options']['windowSizeSubmitSM']=body['submit_options']['windowSizeSubmitSM']
        
    #request['submit_options']['quantityBindSessions']=1
    #if 'quantityBindSessions' in body['submit_options']:
    #    request['submit_options']['quantityBindSessions']=body['submit_options']['quantityBindSessions']

    request['message'] = defaultdict(dict)

    request['message']['service_type']=""
    if 'service_type' in body['message']:
        request['message']['service_type']=body['message']['service_type']
    request['message']['source_addr']=""
    if 'source_addr' in body['message']:
        request['message']['source_addr']=body['message']['source_addr']
    request['message']['source_addr_ton']=0
    if 'source_addr_ton' in body['message']:
        request['message']['source_addr_ton']=body['message']['source_addr_ton']
    request['message']['source_addr_npi']=0
    if 'source_addr_npi' in body['message']:
        request['message']['source_addr_npi']=body['message']['source_addr_npi']
    request['message']['esm_class']=0
    if 'esm_class' in body['message']:
        request['message']['esm_class']=body['message']['esm_class']
    request['message']['protocol_id']=0
    if 'protocol_id' in body['message']:
        request['message']['protocol_id']=body['message']['protocol_id']
    request['message']['priority_flag']=0
    if 'priority_flag' in body['message']:
        request['message']['priority_flag']=body['message']['priority_flag']
    request['message']['schedule_delivery_time']=""
    if 'schedule_delivery_time' in body['message']:
        request['message']['schedule_delivery_time']=body['message']['schedule_delivery_time']
    request['message']['validity_period']=""
    if 'validity_period' in body['message']:
        request['message']['validity_period']=body['message']['validity_period']
    request['message']['registered_delivery']=0
    if 'registered_delivery' in body['message']:
        request['message']['registered_delivery']=body['message']['registered_delivery']
    request['message']['replace_if_present_flag']=0
    if 'replace_if_present_flag' in body['message']:
        request['message']['replace_if_present_flag']=body['message']['replace_if_present_flag']
    request['message']['data_coding']=0
    if 'data_coding' in body['message']:
        request['message']['data_coding']=body['message']['data_coding']

    request['message']['short_message'] = defaultdict(dict)

    request['message']['short_message']['text']=""
    if 'text' in body['message']['short_message']:
        request['message']['short_message']['text']=body['message']['short_message']['text']
    #request['message']['short_message']['ucs2']=""
    #if 'ucs2' in body['message']['short_message']:
    #    request['message']['short_message']['ucs2']=body['message']['short_message']['ucs2']
    #request['message']['short_message']['base64']=""
    #if 'base64' in body['message']['short_message']:
    #    request['message']['short_message']['base64']=body['message']['short_message']['base64']
    #request['message']['tlvs']=""
    #if 'tlvs' in body['message']:
    #    request['message']['tlvs']=body['message']['tlvs']

    request['destinations'] = defaultdict(dict)

    if 'destinations' in body:
        request['destinations']=body['destinations']

    #

    try:
        client = smpplib.client.Client(request['smpp_account_config']['host'], request['smpp_account_config']['port'])
        
        client.set_message_sent_handler( submitsmresp_handler )
        client.set_error_pdu_handler( ml_error_handler )
        
        client.connect()
    except:
        return log_err ("Unable to connect","Unable to connect.\n{}".format(traceback.format_exc()))
        
    try:
        client.bind_transmitter(system_id=request['smpp_account_config']['system_id'], password=request['smpp_account_config']['password'], system_type=request['smpp_account_config']['system_type'])
    except:
        return log_err ("Unable to bind","Unable to bind.\n{}".format(traceback.format_exc()))
        
    #
    
    parts, encoding_flag, msg_type_flag = smpplib.gsm.make_parts(request['message']['short_message']['text'])
    
    submitCount = 0
    
    for dest in request['destinations']:
        for part in parts:
            pdu = client.send_message(
                source_addr=request['message']['source_addr'],
                destination_addr=dest,
                short_message=part,
                data_coding=encoding_flag,
                esm_class=msg_type_flag)
            submitCount+=1
            
    while resultCount != submitCount:
        client.read_once()
        result_available.wait(timeout=0.1)
        
    client.unbind()
    client.disconnect()

    #
        
    messageID = []
    messageIDSorteddict = collections.OrderedDict(sorted(messageIDdict.items()))
    for k, v in messageIDSorteddict.items():
        messageID.append(v)

    #

    return {
        'statusCode': 200,
        'body': json.dumps(
            {'transactionID' : transactionID,
            'messageID' : messageID})
    }
