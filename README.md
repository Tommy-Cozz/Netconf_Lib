PLEASE NOTE: THIS IS EARLY IN DEVELOPMENT, I wanted to be able to push across mlutiple VMs that i work on. However this is for uniformity across the devices.


Current Status: Only TLS connection is working if you come across this and need to update the certificates please find the cert_name cert key and trusted ca in
the tls_engine_init.py folder they are at the top. Change these to match the current PKI infrastructure that you have. 


This uses the following Libraries: socket, ssl, logging, and xml.etree.ElementTree, os, and time


