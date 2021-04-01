# mlrestsmpp
REST-SMPP bridge from Melrose Labs that can be deployed on AWS API Gateway and AWS Lambda

Use REST calls to submit SMS text messages using an [SMPP](https://smpp.org) account. For use with any SMS gateway / aggregator / SMPP provider and not only [Melrose Labs Tyr SMS Gateway](https://melroselabs.com/services/tyr-sms-gateway/).

Deploy in your own AWS API Gateway/Lambda instance or use existing [Melrose Labs](https://melroselabs.com) endpoint (no account required):

``` https://api.melroselabs.com/restsmpp/sms/ ```

API Gateway calls lambda function lambda_function.py to process REST call JSON payload and perform SMPP session.  Multiple destination mobile number can be specified.  Initial code in repository and will be updated with more capabilities and parameters in due course.

## REST API Usage

```
curl --location --request POST https://api.melroselabs.com/restsmpp/sms/ \
	--header 'Content-Type: application/json' \
	--data-raw '{"smpp_account_config":{"host":"HOST","port":2775,"system_id":"SYSTEMID","password":"PASSWORD"},"message":{"source_addr":"MelroseLabs","short_message":{"text":"Melrose Labs engineer great communication services."}},"destinations":["447892000000","44","447892000002","44","44","447892000003"]}'
```

## JSON Request

```
{
  "smpp_account_config": {
    "host": "HOST",
    "port": 2775,
    "system_id": "SYSTEMID",
    "password": "PASSWORD"
  },
  "message": {
    "source_addr": "MelroseLabs",
    "short_message": {
      "text": "Melrose Labs engineer great communication services."
    }
  },
  "destinations": [
    "447892000000",
    "44",
    "447892000002",
    "44",
    "44",
    "447892000003"
  ]
}
```

## Response

Successful (with missing message IDs where rejected):
<pre>
{"transactionID": "39aca5bf-2c5f-4886-bb1f-95ffe4398257", "messageID": ["10a2", "", "10a3", "", "", "10a4"]}
</pre>

Can't connect to host/port:
<pre>
{"error": "Unable to connect"}
</pre>

System ID / password / system type incorrect:
<pre>
{"error": "Unable to bind"}
</pre>
