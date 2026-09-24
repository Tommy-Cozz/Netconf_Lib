"""
GOAL OF THIS py Script
establish a TLS connection with the RU 
 - Be able to control which TLS version is being used v1.2/v1.3
 - Be able to select the specific cipher to use to connect to verify that the radio can in fact support that connection
 - Document the reaction from the radio and verify the correct actions were taken when certian paramters were set (i.e TLS v1.2 was succesfful or cipher was selceted correctly)

"""

import socket
import ssl
import logging

#Setup Variables
#RU_ip = "192.168.150.81"
#RU_ip = "fd17:625c:f037:5::e6"
#RU_ip = "192.168.15.30"

#BIU-D .86
#RU_ip = "fd17:625c:f037:5::94"


#BIU-D .90
# RU_ip = "fd17:625c:f037:5:2a0:aff:fe01:4d93"
RU_ip = "fd17:625c:f037:5::84"

RU_port = 6513


#Testing dual band radio 
#client_cert = "/home/kali/Desktop/Dual_Band_Certs_Testing_VNC_2/vendor-ca.crt"
#client_key = "/home/kali/Desktop/Dual_Band_Certs_Testing_VNC_2/vendor-ca.key"
#CA_cert = "/home/kali/Desktop/Dual_Band_Certs_Testing_VNC_2/vendor-ca.crt"


#client_cert = "/home/kali/Desktop/Dual_Band_Radio_Certs_2/vendor-ca.crt"
#client_key = "/home/kali/Desktop/Dual_Band_Radio_Certs_2/vendor-ca.key"
#CA_cert = "/home/kali/Desktop/Dual_Band_Radio_Certs_2/ca-chain.crt"



#Testing BIU 
# client_cert = "/home/kali/Desktop/BIU_86_CERTIFICATES/vendor-ca.crt"
# client_key = "/home/kali/Desktop/BIU_86_CERTIFICATES/vendor-ca.key"
# CA_cert = "/home/kali/Desktop/BIU_86_CERTIFICATES/vendor-ca.crt"

#Testing the SMO Client
client_cert = "/home/kali/Desktop/AIRSPAIN_OPERATOR_COPY_BACKUP/DU_USER/DU_CERTS/DU_user.crt"
client_key = "/home/kali/Desktop/AIRSPAIN_OPERATOR_COPY_BACKUP/DU_USER/DU_CERTS/du_user.key"
CA_cert = "/home/kali/Desktop/AIRSPAIN_OPERATOR_COPY_BACKUP/operator-ca.crt"



#incorrect_client_cert = "/home/kali/Desktop/PC_ca_test/vendor-ca.crt"


#Establishing the TLS Version 
#TLS_v1_2 = ssl.PROTOCOL_TLSv1_2
#TLS_v1_3 = ssl.PROTOCOL_TLSv1_3

#Cipher = "ECDHE-RSA-AES256-GCM-SHA384" #Can select sepcific cipher to be used

#Cipher list more secure

cipher_list_tls_v_1_2 = ["ECDHE-ECDSA-AES128-SHA256",
                         "ECDHE-RSA-AES128-SHA256",
                         "AES128-GCM-SHA256"
                         "AES128-SHA256",
                         "ECDHE-ECDSA-AES256-GCM-SHA384",
                         "ECDHE-ECDSA-AES256-SHA384",
                         "ECDHE-RSA-AES256-GCM-SHA384",
                         "ECDHE-RSA-AES256-SHA384", 
                         "AES256-GCM-SHA384",
                         "AES256-SHA256"]

cipher_list_tlsv_1_2_sha1 = []

cipher_list_tls_v_1_3 = [
		"AES_256_GCM_SHA384",
		"CHACHA20_POLY1305_SHA256",
		"AES_128_GCM_SHA256",
        ]

#Create the context for the connection 
#context = ssl.SSLContext(TLS_v1_2)
#context = ssl.SSLContext(ssl.PROTOCOL_TLSv1_1)

#UNCOMMNENT TO GET TLSV1.3
context = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
# context.minimum_version = ssl.TLSVersion.TLSv1_3

#UNCOMMENT TO USE TLSV1.1
#context = ssl.create_default_context()
#context = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
#context.maximum_version = ssl.TLSVersion.TLSv1_1



try:
   context.minimum_version = ssl.TLSVersion.TLSv1_2
   context.maximum_version = ssl.TLSVersion.TLSv1_2
except AttributeError:
   context.options |= ssl.OP_NO_SSLv2 | ssl.OP_NO_SSLv3
   context.options |= ssl.OP_NO_TLSv1 | ssl.OP_NO_TLSv1


context.load_cert_chain(certfile=client_cert, keyfile=client_key)
#context.load_verify_locations(CA_cert)
context.load_verify_locations(CA_cert)
context.verify_mode = ssl.CERT_REQUIRED
context.check_hostname = False

#Limit to one Cipher suite (Check for support for each cipher (List of ciphers to chose will come later) 
selected = input("Num_Cipher:")
num_select = int(selected)
cipher_select = cipher_list_tls_v_1_2[num_select]

#NOTE YOU CAN CHOOSE CIPHERS BUT MOST CIPHERS CANNOT BE SLECETED FOR TLSv1.3 ALL CIPHERS ARE ENABLED BY DEFAULT AND ALL AES-GCM and ChaCha20 cipher suites are enabled by dfeauly
#cipher_select = cipher_list_tls_v_1_3[num_select]

#Cipher = "ECDHE-ECDSA-AES256-SHA"

# context.set_ciphers(cipher_select)
#Logging information 
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger("ncclient")
logger.setLevel(logging.DEBUG)
print(logger)

#Create the socket to connect to the server and make the socket TLS 
sock = socket.create_connection((RU_ip, RU_port))
tls_sock = context.wrap_socket(sock, server_hostname=RU_ip)

print(f"Connected to the RU at {RU_ip}:{RU_port} using {tls_sock.version()} with {tls_sock.cipher()}")



#TO verify connection establihsed send NETCONF XML 
message = b"<hello>TESTING CONNECTION</hello>"
tls_sock.sendall(message)


data = tls_sock.recv(4096)
print("Recieved:", data.decode(errors="ignore"))


breakpoint()
tls_sock.close()



