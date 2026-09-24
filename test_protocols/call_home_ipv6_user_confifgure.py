import socket
import ssl
import xml.etree.ElementTree as ET
import time
import logging


#RU INFORMATION AND CERTFIIACTES FOR US CONNECTING 
# RU_ip = "fd17:625c:f037:5::95"
RU_ip = "fd17:625c:f037:10::73"
RU_port = 6513
LISTEN_IP = "fd17:625c:f037:5::1"
LISTEN_PORT = 4335
ALLOWED_RU = "fd17:625c:f037:10::73"

client_cert = "/home/kali/Desktop/PKI_CRL_INFRASTRUCTURE_IN_USE-EST-8_17_26/du_user_crl/oran_du_crl.crt"
client_key = "/home/kali/Desktop/PKI_CRL_INFRASTRUCTURE_IN_USE-EST-8_17_26/du_user_crl/oran_du_crl.key"
CA_cert = "/home/kali/Desktop/PKI_CRL_INFRASTRUCTURE_IN_USE-EST-8_17_26/operator-ca.crt"


import socket
import ssl
import xml.etree.ElementTree as ET
import time
import logging


NETCONF_EOM = b"]]>]]>"  #The b signifies bytes as this is going to be used to detect the end of the bit stream in the TCP pipeline 

logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s | %(name)s | %(levelname)s | %(message)s"
)
log = logging.getLogger("call_home")


#Creat the TLS context and return ctx (This is neccessary for upgrading our normal TCP socket to TLS socket)
def build_tls_context()-> ssl.SSLContext: #-> is nothign special just letting the compiler know that we expect to return the contex tot be used in teh SSLContext function
    ctx = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
    ctx.load_cert_chain(certfile=client_cert, keyfile=client_key)
    ctx.load_verify_locations(CA_cert)
    ctx.verify_mode = ssl.CERT_REQUIRED
    ctx.check_hostname = False
    return ctx


def send_hello_rpc(sock):
   hello = """<?xml version="1.0" encoding="UTF-8"?>
<hello xmlns="urn:ietf:params:xml:ns:netconf:base:1.0">
  <capabilities>
    <capability>urn:ietf:params:netconf:base:1.0</capability>
  </capabilities>
</hello>
"""
   sock.sendall(hello.encode() + NETCONF_EOM)
   print("sent Client Hello")   


def recv_unitl_eom(sock):
   data = b""
   while NETCONF_EOM not in data:
      chunk =sock.recv(4096)
      if not chunk: 
         break
      data += chunk 
   message = data.replace(NETCONF_EOM, b"")
   return message.decode()


def send_rpc_duuser_config(sock):
    o_ran_add_oranduuser = """<?xml version='1.0' encoding='utf-8'?>
<rpc xmlns="urn:ietf:params:xml:ns:netconf:base:1.0" message-id="1">
  <edit-config>
    <target>
      <running/>
    </target>
    <config>
      <o-ran-usermgmt:users xmlns:o-ran-usermgmt="urn:o-ran:user-mgmt:1.0">
        <o-ran-usermgmt:user>
          <o-ran-usermgmt:name>oranduuser@ericcson.com</o-ran-usermgmt:name>
          <o-ran-usermgmt:account-type>CERTIFICATE</o-ran-usermgmt:account-type>
          <o-ran-usermgmt:enabled>true</o-ran-usermgmt:enabled>
        </o-ran-usermgmt:user>
      </o-ran-usermgmt:users>
    </config>
  </edit-config>
</rpc>
"""
    o_ran_add_cert_to_name_fingerprint_oranduuser = """<?xml version='1.0' encoding='utf-8'?>
<rpc xmlns="urn:ietf:params:xml:ns:netconf:base:1.0" message-id="1">
  <edit-config>
    <target>
      <running/>
    </target>
    <config>
      <o-ran-cert:certificate-parameters xmlns:o-ran-cert="urn:o-ran:certificates:1.0">
        <o-ran-cert:cert-maps>
          <o-ran-cert:cert-to-name>
            <o-ran-cert:id>1</o-ran-cert:id>
            <o-ran-cert:fingerprint>04:E1:B4:E9:50:47:07:B5:13:46:04:21:7D:DB:12:85:92:22:64:93:43:A5:FB:AC:1A:8A:B3:E1:74:10:F7:8D:13</o-ran-cert:fingerprint>
            <o-ran-cert:map-type xmlns:x509c2n="urn:ietf:params:xml:ns:yang:ietf-x509-cert-to-name">x509c2n:san-rfc822-name</o-ran-cert:map-type>
          </o-ran-cert:cert-to-name>
        </o-ran-cert:cert-maps>
      </o-ran-cert:certificate-parameters>
    </config>
  </edit-config>
</rpc>"""

    ietf_network_access_control_management = """<?xml version='1.0' encoding='utf-8'?>
<rpc xmlns="urn:ietf:params:xml:ns:netconf:base:1.0" message-id="2">
  <edit-config>
    <target>
      <running/>
    </target>
    <config>
      <nacm:nacm xmlns:nacm="urn:ietf:params:xml:ns:yang:ietf-netconf-acm">
        <nacm:groups>
          <nacm:group>
            <nacm:name>sudo</nacm:name>
            <nacm:user-name>oranduuser@ericcson.com</nacm:user-name>
          </nacm:group>
        </nacm:groups>
      </nacm:nacm>
    </config>
  </edit-config>
</rpc>
"""

    sock.sendall(o_ran_add_cert_to_name_fingerprint_oranduuser.encode() + NETCONF_EOM)
    print("ORAN_DU_FINGERPRINT_CONFIGURED FOR: oranduuser@ericcson.com")
    reply = recv_unitl_eom(sock)
    print("\n|-----REPLY FINGERPRINT-----|")
    print(reply)
    time.sleep(2)

    sock.sendall(o_ran_add_oranduuser.encode() + NETCONF_EOM)
    print("Configuring O_RAN_USER")
    reply = recv_unitl_eom(sock)
    print("\n|-----REPLY USER-----|")
    print(reply)
    time.sleep(2)

    sock.sendall(ietf_network_access_control_management.encode() + NETCONF_EOM)
    print("Configuring NACM")
    reply = recv_unitl_eom(sock)
    print("\n|-----REPLY NACM-----|")
    print(reply)
    time.sleep(2)

def send_rpc_smo_user_config(sock):
    o_ran_add_smouser = """<?xml version='1.0' encoding='utf-8'?>
<rpc xmlns="urn:ietf:params:xml:ns:netconf:base:1.0" message-id="0">
  <edit-config>
    <target>
      <running/>
    </target>
    <config>
      <o-ran-usermgmt:users xmlns:o-ran-usermgmt="urn:o-ran:user-mgmt:1.0">
        <o-ran-usermgmt:user>
          <o-ran-usermgmt:name>oransmouser@ericsson.com</o-ran-usermgmt:name>
          <o-ran-usermgmt:account-type>CERTIFICATE</o-ran-usermgmt:account-type>
          <o-ran-usermgmt:enabled>true</o-ran-usermgmt:enabled>
        </o-ran-usermgmt:user>
      </o-ran-usermgmt:users>
    </config>
  </edit-config>"""
    o_ran_add_cert_to_name_fingerprint_smouser = """<?xml version='1.0' encoding='utf-8'?>
<rpc xmlns="urn:ietf:params:xml:ns:netconf:base:1.0" message-id="1">
  <edit-config>
    <target>
      <running/>
    </target>
    <config>
      <o-ran-cert:certificate-parameters xmlns:o-ran-cert="urn:o-ran:certificates:1.0">
        <o-ran-cert:cert-maps>
          <o-ran-cert:cert-to-name>
            <o-ran-cert:id>2</o-ran-cert:id>
            <o-ran-cert:fingerprint>04:E1:B4:E9:50:47:07:B5:13:46:04:21:7D:DB:12:85:92:22:64:93:43:A5:FB:AC:1A:8A:B3:E1:74:10:F7:8D:13</o-ran-cert:fingerprint>
            <o-ran-cert:map-type xmlns:x509c2n="urn:ietf:params:xml:ns:yang:ietf-x509-cert-to-name">x509c2n:san-rfc822-name</o-ran-cert:map-type>
          </o-ran-cert:cert-to-name>
        </o-ran-cert:cert-maps>
      </o-ran-cert:certificate-parameters>
    </config>
  </edit-config>
</rpc>"""

    ietf_network_access_control_management_smo_user = """<?xml version='1.0' encoding='utf-8'?>
<rpc xmlns="urn:ietf:params:xml:ns:netconf:base:1.0" message-id="0">
  <edit-config>
    <target>
      <running/>
    </target>
    <config>
      <nacm:nacm xmlns:nacm="urn:ietf:params:xml:ns:yang:ietf-netconf-acm">
        <nacm:groups>
          <nacm:group>
            <nacm:name>smo</nacm:name>
            <nacm:user-name>oransmouser@ericsson.com</nacm:user-name>
          </nacm:group>
        </nacm:groups>
      </nacm:nacm>
    </config>
  </edit-config>
</rpc>
"""
    
  

    sock.sendall(o_ran_add_smouser.encode() + NETCONF_EOM)
    print("Configuring SMO User")
    reply = recv_unitl_eom(sock)
    print("\n|-----REPLY NACM-----|")
    print(reply)
    time.sleep(2)
    
    sock.sendall(ietf_network_access_control_management_smo_user.encode() + NETCONF_EOM)
    print("Configuring NACM")
    reply = recv_unitl_eom(sock)
    print("\n|-----REPLY NACM-----|")
    print(reply)
    time.sleep(2)
    
    sock.sendall(o_ran_add_cert_to_name_fingerprint_smouser.encode() + NETCONF_EOM)
    print("Configuring NACM")
    reply = recv_unitl_eom(sock)
    print("\n|-----REPLY NACM-----|")
    print(reply)
    time.sleep(2)


def call_home_listener():
    ctx = build_tls_context()
    srv = socket.socket(socket.AF_INET6, socket.SOCK_STREAM)
    srv.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    srv.bind((LISTEN_IP, LISTEN_PORT, 0, 0))
    srv.listen(5)
    log.info(f"Listening for call-home on [{LISTEN_IP}]:{LISTEN_PORT}")

    while True:
        raw_client, addr = srv.accept()
        ru_addr = addr[0]
        log.info(f"Inbound TCP from: {ru_addr}")

        if ru_addr != ALLOWED_RU:
            log.warning(f"Rejected — not expected RU: {ru_addr}")
            raw_client.close()
            continue

        try:
            
            tls_sock = ctx.wrap_socket(raw_client, server_side=False)
            log.info(f"TLS established | version={tls_sock.version()} | cipher={tls_sock.cipher()}")
            

            
            send_hello_rpc(tls_sock)
            time.sleep(2)
            
            
            send_rpc_duuser_config(tls_sock)
            time.sleep(2)
            print("---------------------------")
            #send_rpc_smo_user_config(tls_sock)
            subscribe(tls_sock)
            watchdog_timer_reset(tls_sock)

            time.sleep(2000)
            tls_sock.close()


        except Exception as e:
            print(e)
            tls_sock.close()
            break

def send_verify_rpcs(sock):
    cert_to_name_verify = """<?xml version='1.0' encoding='utf-8'?>
<rpc xmlns="urn:ietf:params:xml:ns:netconf:base:1.0" message-id="0">
  <get>
    <filter type="subtree">
      <o-ran-cert:certificate-parameters xmlns:o-ran-cert="urn:o-ran:certificates:1.0">
        <o-ran-cert:cert-maps>
          <o-ran-cert:cert-to-name/>
        </o-ran-cert:cert-maps>
      </o-ran-cert:certificate-parameters>
    </filter>
  </get>
</rpc>"""
    user_management_verify="""<?xml version='1.0' encoding='utf-8'?>
<rpc xmlns="urn:ietf:params:xml:ns:netconf:base:1.0" message-id="1">
  <get>
    <filter type="subtree">
      <o-ran-usermgmt:users xmlns:o-ran-usermgmt="urn:o-ran:user-mgmt:1.0"/>
    </filter>
  </get>
</rpc>
"""
    user_group_verify="""<?xml version='1.0' encoding='utf-8'?>
<rpc xmlns="urn:ietf:params:xml:ns:netconf:base:1.0" message-id="2">
  <get>
    <filter type="subtree">
      <nacm:nacm xmlns:nacm="urn:ietf:params:xml:ns:yang:ietf-netconf-acm">
        <nacm:groups/>
      </nacm:nacm>
    </filter>
  </get>
</rpc>
"""
    sock.sendall(user_group_verify.encode() + NETCONF_EOM)
    print("\n|------VERIFY USER GROUP--------|")
    reply = recv_unitl_eom(sock)
    print("\n|------REPLY USER GROUP GET----|")
    print(reply)


    sock.sendall(user_group_verify.encode() + NETCONF_EOM)
    print("\n|------VERIFY USER GROUP--------|")
    reply = recv_unitl_eom(sock)
    print("\n|------REPLY USER GROUP GET----|")
    print(reply)

def subscribe(sock):
  start_supervision = """
  <?xml version="1.0" encoding="UTF-8"?>
<rpc xmlns="urn:ietf:params:xml:ns:netconf:base:1.0" message-id="e36626dd-6b22-11f1-9119-9acd959bc434">
  <ncEvent:create-subscription xmlns:ncEvent="urn:ietf:params:xml:ns:netconf:notification:1.0"/>
</rpc>
  """
  sock.sendall(start_supervision.encode() + NETCONF_EOM)
  print("\n|-------STARTED SUPERVISION---------|")
  reply=recv_unitl_eom(sock)
  print(f"\n {reply}")
  
def watchdog_timer_reset(sock):
  set_timer= """"
    <?xml version="1.0" encoding="UTF-8"?>
<rpc xmlns="urn:ietf:params:xml:ns:netconf:base:1.0" message-id="3426b3ac-6b23-11f1-96aa-9acd959bc434">
  <o-ran-supervision:supervision-watchdog-reset xmlns:o-ran-supervision="urn:o-ran:supervision:1.0">
    <o-ran-supervision:supervision-notification-interval>60000</o-ran-supervision:supervision-notification-interval>
    <o-ran-supervision:guard-timer-overhead>250</o-ran-supervision:guard-timer-overhead>
  </o-ran-supervision:supervision-watchdog-reset>
</rpc>
  """
  sock.sendall(set_timer.encode() + NETCONF_EOM)
  print("\n|-------STARTED SUPERVISION---------|")
  reply=recv_unitl_eom(sock)
  print(f"\n {reply}")
  
def recconect_configure_smo_user():
    log.info(f"[SESSION 2 Recconection: Verify User Config Success")
    ctx = build_tls_context()
    raw = socket.create_connection((ALLOWED_RU, RU_port))
    tls = ctx.wrap_socket(raw, server_hostname=ALLOWED_RU)
    log.info(f"[SESSION 2 ESTABLISHED] TLS UP \n Version:{tls.version()} \n Negotiated Cipher: {tls.cipher()}")

    send_hello_rpc(tls)
    send_rpc_smo_user_config(tls)
    print("Configured ")
    tls.close()


def main():
    call_home_listener()
    time.sleep(2)
    print("[*] Configuring SMO user")
    

  
if __name__ == "__main__":
    main()





