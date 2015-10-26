# OMA LWM2M

## Background

 - Need for a lightweight protocol as more & more devices are constrained
 - No  standardized solution

Open Mobile Alliance Device Management is widely used 
LWM2M is a reboot of OMA DM targeting M2M

### OMA DM
 - HTTP/XML binary encoded
 - HMAC MD5 for authentication
 - HTTPS if security is needed

One stack for the device management & Application data
designed to be used on top of COAP or SMS

Released in 2003

## Built on COAP ?

 - COAP overhead : 8 bytes
 - QOS : two types
  + confirmable message
  + Or not

COAP is RESTful : GET coap://myhouse.iot/bedroom/lamps/7/status
HTTP verbs : GET, POST, PUT, DELETE
1 more verb : observe (suscribe)
All in a binary format.

Easily translatable to HTTP, Web-like caching

## What does LWM2M it do ?

### Device Management

 - Firmware + application upgrade
 - Bootstraping
 - Configure the device
 - Monitor connectivity
 - Reboot, reset to factory
 - Rrotate security keys

## What's in the Client ?

Standard objects defined by OMA. Objects have a numérical identifier (16bits integer)
Objects are registered by the OMA Naming authority
Defining a new object is possible via submitting an form to the OMA.

### Objects ?

 - Each object may have multiple instances (ID = 8 bits integer)
 - Objects contains resources 
  * ID = 16 bits integer
  * Atomic piece of information with a data-type (string, integer...)
  * Can be READ, WRITE, EXECUTED, DELETED or OBSERVED

 An access control object allow you to restrict permitions on resources
 Ex :
 * Location object 
  - Latitude = Read Only
  - Longitude = Read Only
  - Altitude = Read Only
 * Device object
  - Manufacturer = Read Only
  - Timestamp = Read & Write
  - Reboot = Execute

These ressources can be acceced by a tree structure : /objectID/instanceID/ressourceID


### Management objects !

Defined by OMA
 
 - Device
 - Server
 - Connectivity Monitoring
 - Connectivity Statistic
 - Lock And Wipe
 - Location 
 - Firmware 
 - Access Control 
 - Security
 - etc...

 Or 3rd Party

### Application objects !

Contain the value you need for your application.
Define your own or use the already evailable ones.

### IPSO Objects
IPSO already defined the basic things you need for common devices.
http://technical.openmobilealliance.org/Technical/technical-information/omna/lightweight-m2m-lwm2m-object-registry

#### Ex : Luminance sensor : ID 3301
 - Sensor Value
 - Units
 - Min. Measured Value
 - Max. Measured Value
 - Min. Range Value
 - Max. Range Value
 - Reset Min. & Max. Measured Values


## How does the server & the client talk .


## What's on the wire ?


## Security

Three security modes : PSK & Public KEy mode & Certificate.