# Internet of Things :  devices to cloud landscape

In this document I will *try* to list the major cloud providers for the IoT.


## Amazon Web Services for IOT

[Main documentation page](http://docs.aws.amazon.com/iot/latest/developerguide/what-is-aws-iot.html)

The devices can communicate with the cloud via :
 + HTTP
 + MQTT

**Confidentiality** is provided by **TLS** and must be used at every point.   
Various TLS ciphers are [suported](http://docs.aws.amazon.com/iot/latest/developerguide/iot-security-identity.html)    

**Authentication** is provided by [sigV4 Amazon's certificates](http://docs.aws.amazon.com/general/latest/gr/signature-version-4.html).   

**Authorization** is managed via policies for users, groups, and roles.
Those policies are linked to identies. Identities can be created via the [Identity & Access Management](https://aws.amazon.com/fr/iam/)    
Policies can also be linked to an [Amazon Cognito identy](https://docs.aws.amazon.com/cognito/devguide/identity/) or any [OpenID Connect provider](https://docs.aws.amazon.com/cognito/devguide/identity/external-providers/openid-connect/) (facebook, Google...)

No device management is offered.    
Devices have the responsability to keep their credentials, no provisionning mechanism is offered (X509 private keys should be burned in the client - TLSv1.2 & SHA-256 RSA certificate signature validation MUST be supported-).
The devices have to be declared in the AWS registry database (devices public keys). A CLI-tool is provided to manage identities and roles for each device (create, activate, desactivate, revoke).    


## Rhiot
[Red Hat IoT solution](http://rhiot.io)
[Documentation](https://github.com/rhiot/rhiot/blob/master/docs/readme.md)

The device exchange data with the cloud via :
 - MQTT
 - HTTP
 - LWM2M (COAP)
 - AMQP

**Device management** : Rhiot offers a [LWM2M](LWM2M/LWM2M.md) implementation to manage de device. Device details can be accessed this way. [see here](https://github.com/rhiot/rhiot/blob/master/docs/readme.md#reading-devices-details)
Boostraping solution : server initiated, must be on the same network.

**Authentication** (optional). HTTP requests are intercepted to add a token support. [Not built-in.](https://github.com/rhiot/rhiot/blob/master/docs/readme.md#intercepting-rest-api-requests)

**Confidentiality** (optional). TLS can be activated.

**Authorization** not implemented. However LWM2M offers an access control object, so that should work easily.


## Microsoft azure iot hub
AMQP -> SASL PLAIN  & AMQP Claim based security.
MQTT
HTTP
Per device auth & security.
TLS ?
SAS . look a the C code samples to understand how do they authenticate (sas in amqp??)



## OVH iot -> Still in Beta (see runabove.com)
auth via token (got into your runabove account) + TLS
--> differents tokens for write & access
HTTPS (POST)
telnet ('put' command)
As for now the system send an ACK (http) or a 'go' to send (telnet)


## thingworx
TLS 1.2
The devices needs to authenticate (how?)


## Zatar 
Application : Authentication : get a token via HTTPS POST (email&password)
	read & write data via HTTPS API.
Device : CoAP (UDP or TCP) with TLS or DTLS.


## SierraWireless
 - AirVantage is the cloud plateform
  * Device send data to cloud via MQTT or HTTP API.
  * Application can access the data via HTTPS API

 - Gateways
  * Can be managed via AirLink service
  * 

## Texas Instruments
SensorTag

## Onion IOT (they also sell a little raspberry pi less powerful.)
Auth 2.0 
RESTful API
Low-end devices can use 128 bits AES. SSL otherwise


## IBM Bluemix
act as the MQTT broker
you declare your device into the plateform, then get a token that you push into the device.
You want security ? Use TLS. No UDP support.

## DELL 
wants to offer gateways that brings the intelligence of the cloud at the edge of the devices network
announced 21 oct.
