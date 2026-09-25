import sys 
import os
import subprocess
from tls_engine_init import *

"""
Prupose of this script is to create a user configure them to match with certificate from certificate finger print (ROOT CA)
and map that user to the respective group defined in the NACM
"""

    
tls = gen_tls()
netconf_tls = gen_NETCONF_TLS()
tls_sock = netconf_tls.direct_tls_connect()

netconf = create_netconf_session(tls_sock)
print(f"Connected to the RU at {RU_ip}:{RU_port} using {tls_sock.version()} with {tls_sock.cipher()}")

target_key = input("Enter the modified Yang Param you wish to edit: I.E(create_subscription OR watchdog)")
if target_key in RPC_SENDS:
    user_interavel = input("Enter the Supervision notification interval value: ")
    user_gaurd = input("Gaurd Timer value: ")
    raw_template = RPC_SENDS[target_key]
    formatted_xml = raw_template.format(interval=user_interavel,gaurd=user_gaurd)
    print("-----Generated XML PAYLOAD----\n")
    print(formatted_xml)
    

netconf.send_hello()
netconf.send_rpc(RPC_SENDS["create_subscription"])
netconf.send_rpc(formatted_xml)
#Definign a way to have custom input in the RPCS
time.sleep(int(user_interavel))
