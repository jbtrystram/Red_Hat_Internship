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


## Microsoft Azure IoT
[Main Documentation](https://azure.microsoft.com/en-us/documentation/articles/iot-hub-what-is-azure-iot/)   
[Technical Documentation](https://azure.microsoft.com/en-us/documentation/articles/iot-hub-devguide/)   
[SDKs](https://github.com/Azure/azure-iot-sdks)   

The device exchange data with the cloud via :    
 - AMQP
 - HTTP
 - MQTT ([via Azure protocol gateway](https://azure.microsoft.com/en-us/documentation/articles/iot-hub-devguide/#messaging))

*Note* : Your application can access devices via the Azure hub only with **AMQP**.

**Device management** :    
The device must be [provisioned in the IoT hub](https://azure.microsoft.com/en-gb/documentation/articles/iot-hub-device-management/#device-provisioning-and-discovery). The service issue the necessary tokens and URIs. Thoses must be provided into the device.
The service offers a REST API to create, retrieve, update, and delete devices.

**Authentication**    
 - SASL PLAIN & Claim based security when using AMQP
 - Token in the Authentication HTTP header

**Confidentiality** : TLS must always be use.

**Authorization** Per device policy. Read/Write/Connect.


## OVH iot (Still in Beta)
runabove.com

Available protocols :    
 - HTTP
 - Telnet

**Authentication**     
Token (got into your runabove account, when provisioning a device) or TLS certificate

**Confidentiality** devices may use TLS encryption

**Authorization**    
differents tokens are used to write or read.

## IBM Bluemix
[Main documentation](https://docs.internetofthings.ibmcloud.com/fr/index.html)
IBM bluemix is based on the open source project [cloud foundry](https://www.cloudfoundry.org/)

Available protocol :
 - MQTT

**Device Management** : IBM offers a custom device management [built on MQTT](https://docs.internetofthings.ibmcloud.com/reference/device_mgmt.html) :
 - Location
 - Device Attributes
 - Diagnostics
 - Observation
 - Reboot / Reset / upgrade firmware

**Confidentiality** devices may use TLS encryption

**Authentication**     
Device must provide its ID + Token (got into your cloud account, when provisioning a device).    
*Note* : the token is not stored in the cloud. You must store it (in case IBM cloud gets hacked?).

**Authorization** : devices can publish and subscribe to a restricted topic space.


## Zatar 
[device API](http://www.zatar.com/device-API)

Available protocols :    
 - COAP (over UDP&TCP)

**Authentication**     ?

**Confidentiality** devices may use TLS or DTLS

**Authorization**    ?


## SierraWireless AirVantage

[Cloud offer](http://www.sierrawireless.com/products-and-solutions/cloud-and-connectivity-solutions/)

Supported protocols :
 - MQTT
 - LWM2M
 - HTTP

**Authentication**   
The device is authenticated via login & password. Those must be provided into the cloud managment interface when the device is declared.

More  details : [Publishing via MQTT](https://doc.airvantage.net/av/howto/hardware/samples/generic-mqtt/)

Sell physical Gateways that can be managed via AirLink service.       
Proxy to google apps engine     