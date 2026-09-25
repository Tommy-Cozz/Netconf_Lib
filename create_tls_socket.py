import socket
import ssl
import xml.etree.ElementTree as ET
import time
import logging

client_cert = "/home/kali/Desktop/PKI_CRL_INFRASTRUCTURE_IN_USE-EST-8_17_26/du_user_crl/oran_du_crl.crt"
client_key = "/home/kali/Desktop/PKI_CRL_INFRASTRUCTURE_IN_USE-EST-8_17_26/du_user_crl/oran_du_crl.key"
CA_cert = "/home/kali/Desktop/PKI_CRL_INFRASTRUCTURE_IN_USE-EST-8_17_26/operator-ca.crt"
NETCONF_EOM = b"]]>]]>"  #The b signifies bytes as this is going to be used to detect the end of the bit stream in the TCP pipeline 

logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s | %(name)s | %(levelname)s | %(message)s"
)
log = logging.getLogger("call_home")

#Create the TLS CAll HOME LISTENER SOCKET


class TLS:
    def __init__(self, certfile, keyfile,CA_cert):
        self.certfile = certfile
        self.keyfile = keyfile
        self.CA_cert = CA_cert
    
    
    def build_tls_context(self)-> ssl.SSLContext: #-> is nothign special just letting the compiler know that we expect to return the contex tot be used in teh SSLContext function
        ctx = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
        ctx.load_cert_chain(certfile=self.certfile, keyfile=self.keyfile)
        ctx.load_verify_locations(self.CA_cert)
        ctx.verify_mode = ssl.CERT_REQUIRED
        ctx.check_hostname = False
        return ctx
    
    def build_custom_tls_context(self) -> ssl.SSLContext:
        ctx = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
        # match tls_ver:
            
        #     case "TLSv1.2":
        #         try:
        #             ctx.minimum_version = ssl.TLSVersion.TLSv1_2
        #             ctx.maximum_version = ssl.TLSVersion.TLSv1_2
        #         except AttributeError:
        #             ctx.options |= ssl.OP_NO_SSLv2 | ssl.OP_NO_SSLv3
        #             ctx.options |= ssl.OP_NO_TLSv1 | ssl.OP_NO_TLSv1
                    
        #     case "TLSv1.3":
        #         try:
        #             ctx.minimum_version = ssl.TLSVersion.TLSv1_3
        #             ctx.maximum_version = ssl.TLSVersion.TLSv1_3
        #         except AttributeError:
        #             ctx.options |= ssl.OP_NO_SSLv2 | ssl.OP_NO_SSLv3
        #             ctx.options |= ssl.OP_NO_TLSv1 | ssl.OP_NO_TLSv1
        try:
            ctx.minimum_version = ssl.TLSVersion.TLSv1_3
            ctx.maximum_version = ssl.TLSVersion.TLSv1_3
        except AttributeError:
            ctx.options |= ssl.OP_NO_SSLv2 | ssl.OP_NO_SSLv3
            ctx.options |= ssl.OP_NO_TLSv1 | ssl.OP_NO_TLSv1
        ctx.load_cert_chain(certfile=self.certfile, keyfile=self.keyfile)
        ctx.load_verify_locations(self.CA_cert)
        ctx.verify_mode = ssl.CERT_REQUIRED
        ctx.check_hostname = False 
        #Will need to add functionality for cipher select however we can just review the advertised ciphers instead
        return ctx
            
    
class NETCONF_TLS:
    def __init__(self, tls, RU_IP, RU_PORT, LISTEN_IP, LISTEN_PORT):
        self.tls = tls
        self.RU_IP = RU_IP
        self.RU_PORT = RU_PORT
        self.LISTEN_IP = LISTEN_IP
        self.LISTEN_PORT = LISTEN_PORT
    
        
    def server_setup(self):
        srv = socket.socket(socket.AF_INET6, socket.SOCK_STREAM)
        srv.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR,1)
        srv.bind((self.LISTEN_IP, self.LISTEN_PORT, 0,0))
        return srv
    
    def direct_tls_connect(self):
        sock = socket.create_connection((self.RU_IP, self.RU_PORT))
        ctx = self.tls.build_custom_tls_context()
        tls_sock = ctx.wrap_socket(sock,server_hostname=self.RU_IP)
        
        return tls_sock
    
    def call_home_listener(self):
        ctx = self.tls.build_tls_context()
        srv = self.server_setup()
        srv.listen(5)
        log.info(f"[INFO] LISTENING FOR CALL HOME ON [{self.LISTEN_IP}]:[{self.LISTEN_PORT}]")
        raw_client, addr = srv.accept()
        
        tls_sock = None
        
        try:
            tls_sock = ctx.wrap_socket(raw_client, server_side=False)
            return tls_sock
            #THES WILL BE HANDLEDED BY THE ESTABLISH NETCONF CLASS send_hello_rpc(tls_sock)
            
            #THES WILL BE HANDLEDED BY THE ESTABLISH NETCONF CLASS subcribe_to_notification(tls_sock)
        except Exception as e:
            print(e)
            print("RU Disconected... Expecting a Reconnection ")
        # finally:
        #     #THES WILL BE HANDLEDED BY THE ESTABLISH NETCONF CLASStime.sleep(supervision_interval)
        #     if tls_sock is not None:
        #         tls_sock.close()

        #     print(
        #         "Closed TLS SOCKET. "
        #         "Cleaning up and waiting for connection from O-RU"
        #     )
class NETCONF_PROTO:
    def __init__(self, tls_sock, NETCONF_EOM):
        self.self = self
        self.tls_sock = tls_sock
        self.NETCONF_EOM = NETCONF_EOM

    def send_hello(self):
        hello = """<?xml version="1.0" encoding="UTF-8"?>
        <hello xmlns="urn:ietf:params:xml:ns:netconf:base:1.0">
        <capabilities>
            <capability>urn:ietf:params:netconf:base:1.0</capability>
        </capabilities>
        </hello>
        """
        self.tls_sock.sendall(hello.encode() + NETCONF_EOM)
        print("[INFO] Sent Client Hello \n")
        ru_reply = self.recv_unitl_eom()
        print(f"[RU_MSG] REPLY: {ru_reply} \n")
    
    def recv_unitl_eom(self):
        data = b""
        while NETCONF_EOM not in data:
            chunk =self.tls_sock.recv(4096)
            if not chunk: 
                break
            data += chunk 
        message = data.replace(self.NETCONF_EOM, b"")
        return message.decode()  
    
    def send_rpc(self,rpc):
        self.tls_sock.sendall(rpc.encode() + self.NETCONF_EOM)
        print(f"\n[INFO] SENDING RPC: {rpc}\n")
        ru_reply = self.recv_unitl_eom()
        print(ru_reply)
    


