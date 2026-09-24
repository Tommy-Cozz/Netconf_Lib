"""
/usr/bin/python3
Purpose of script: 
This script is for workign on creating the default sceanrios as I will end up using a lot of the same things each time 
this will allow the use of the TLS_LIB classes and only allow me to have to worry about importing it once and not in every single new py file 
allowing for the establishment of the base TLS classes and functions to call on to which I would make somethign for example 
tls then netconf tls and that would be good engouh to get the rpcs going 
"""


import sys
import os

#future plans needed to import the argparse lib 
client_cert = "/home/kali/Desktop/PKI_CRL_INFRASTRUCTURE_IN_USE-EST-8_17_26/du_user_crl/oran_du_crl.crt"
client_key = "/home/kali/Desktop/PKI_CRL_INFRASTRUCTURE_IN_USE-EST-8_17_26/du_user_crl/oran_du_crl.key"
CA_cert = "/home/kali/Desktop/PKI_CRL_INFRASTRUCTURE_IN_USE-EST-8_17_26/operator-ca.crt"
#Add the supprot for ivp4 as well as ipv6 (Just an if statement i have the code for that somehwere useing the detec socket type)
RU_ip = "fd17:625c:f037:5::95"
# RU_ip = "fd17:625c:f037:10::73"
RU_port = 6513
LISTEN_IP = "fd17:625c:f037:5::1"
LISTEN_PORT = 4335
ALLOWED_RU = "fd17:625c:f037:5::95"

parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if parent_dir not in sys.path:
    sys.path.append(parent_dir)

from create_tls_socket import *

def gen_tls():
    tls = TLS(client_cert,client_key,CA_cert)
    return tls 

tls = gen_tls()

    
def gen_NETCONF_TLS():
    netconf_tls = NETCONF_TLS(tls,RU_IP=RU_ip,RU_PORT=RU_port,LISTEN_IP=LISTEN_IP,LISTEN_PORT=LISTEN_PORT)
    return netconf_tls

netconf_tls = gen_NETCONF_TLS()

def heartbeat(tls_sock,supervision_timer):
    time.sleep(supervision_timer)

    tls_sock.close()

    print(f"[INFO] Supervision Expired - Opening Call Home Listener for RU at {RU_ip}")

    return netconf_tls.call_home_listener()

def supervise_ru(netconf):
    netconf.send_rpc(rpc=RPC_SENDS["create_subscription"])
    netconf.send_rpc(rpc=RPC_SENDS["watchdog"])
    
def create_netconf_session(tls_sock):
    netconf = NETCONF_PROTO(tls_sock, NETCONF_EOM)
    return netconf


supervision_timer = 30

def establish_ch(netconf_tls):

    tls_sock = netconf_tls.call_home_listener()

    while True:

        netconf = create_netconf_session(tls_sock)
        netconf.send_hello()
        supervise_ru(netconf)
        tls_sock = heartbeat(
            tls_sock,
            supervision_timer
        )

        netconf = create_netconf_session(tls_sock)
        netconf.send_hello()
        supervise_ru(netconf)
        print("[INFO] Supervision Established - Waiting")  

def establish_direct_tls(netconf_tls):
    tls_sock = netconf_tls.direct_tls_connect()
    

        