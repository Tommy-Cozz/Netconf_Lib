from enum import Enum
from create_tls_socket import *



class RPC_ID(Enum):
    WATCHDOG = "watchdog"
    CREATE_SUBSCRIPTION = "create_subscription"
    CALL_HOME = "call_home"
    USER = "user"
    CERT_TO_NAME= "cert_to_name"
    IEEE_8021X = "IEEE_8021x"
    FTPES = "ftpes"
    
RPC_SENDS = {
    "create_subscription": """<?xml version="1.0" encoding="UTF-8"?>
<rpc xmlns="urn:ietf:params:xml:ns:netconf:base:1.0" message-id="465f81f6-adfa-11f1-a1c3-9acd959bc434">
  <ncEvent:create-subscription xmlns:ncEvent="urn:ietf:params:xml:ns:netconf:notification:1.0"/>
</rpc>""",
    
    "watchdog" : """<rpc message-id="101"
 xmlns="urn:ietf:params:xml:ns:netconf:base:1.0">
  <supervision-watchdog-reset
    xmlns="urn:o-ran:supervision:1.0">
    <supervision-notification-interval>{interval}</supervision-notification-interval>
    <guard-timer-overhead>{gaurd}</guard-timer-overhead>
  </supervision-watchdog-reset>
</rpc>
""",

    "user_create" : """<?xml version='1.0' encoding='utf-8'?>
<rpc xmlns="urn:ietf:params:xml:ns:netconf:base:1.0" message-id="1">
  <edit-config>
    <target>
      <running/>
    </target>
    <config>
      <o-ran-usermgmt:users xmlns:o-ran-usermgmt="urn:o-ran:user-mgmt:1.0">
        <o-ran-usermgmt:user>
          <o-ran-usermgmt:name>{username}</o-ran-usermgmt:name>
          <o-ran-usermgmt:account-type>{account_type}</o-ran-usermgmt:account-type>
          <o-ran-usermgmt:enabled>{enabled}</o-ran-usermgmt:enabled>
        </o-ran-usermgmt:user>
      </o-ran-usermgmt:users>
    </config>
  </edit-config>
</rpc>""",

    "cert_to_name" :"""<?xml version='1.0' encoding='utf-8'?>
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
            <o-ran-cert:fingerprint>{crt_fingerprint}}</o-ran-cert:fingerprint>
            <o-ran-cert:map-type xmlns:x509c2n="urn:ietf:params:xml:ns:yang:ietf-x509-cert-to-name">{map_type}</o-ran-cert:map-type>
          </o-ran-cert:cert-to-name>
        </o-ran-cert:cert-maps>
      </o-ran-cert:certificate-parameters>
    </config>
  </edit-config>
</rpc>""",

    "nacm_group" :"""<?xml version='1.0' encoding='utf-8'?>
<rpc xmlns="urn:ietf:params:xml:ns:netconf:base:1.0" message-id="2">
  <edit-config>
    <target>
      <running/>
    </target>
    <config>
      <nacm:nacm xmlns:nacm="urn:ietf:params:xml:ns:yang:ietf-netconf-acm">
        <nacm:groups>
          <nacm:group>
            <nacm:name>{access_group}</nacm:name>
            <nacm:user-name>{user}</nacm:user-name>
          </nacm:group>
        </nacm:groups>
      </nacm:nacm>
    </config>
  </edit-config>
</rpc>""",

    "ietf_interface_config" :"""<rpc xmlns="urn:ietf:params:xml:ns:netconf:base:1.0" message-id="1">
  <edit-config>
    <target>
      <running/>
    </target>
    <config>
      <if:interfaces xmlns:if="urn:ietf:params:xml:ns:yang:ietf-interfaces">
        <if:interface>
          <if:name>{interface_name}</if:name>
          <dot1x:pae xmlns:dot1x="urn:ieee:std:802.1X:yang:ieee802-dot1x">
            <dot1x:pae-system>{pae_system}</dot1x:pae-system>
            <dot1x:port-type>real-port</dot1x:port-type>
            <dot1x:supplicant>
              <dot1x:held-period>{held_period}</dot1x:held-period>
              <dot1x:retry-max>{max_retry}</dot1x:retry-max>
            </dot1x:supplicant>
          </dot1x:pae>
          <if:type xmlns:ianaift="urn:ietf:params:xml:ns:yang:iana-if-type">{iana_interface_type}</if:type>
        </if:interface>
      </if:interfaces>
    </config>
  </edit-config>
</rpc>""",
    "ietf_system_config" :"""<rpc xmlns="urn:ietf:params:xml:ns:netconf:base:1.0" message-id="1">
   <edit-config>
      <target>
         <running/>
      </target>
      <config>
         <sys:system xmlns:sys="urn:ietf:params:xml:ns:yang:ietf-system">
         <dot1x:pae-system xmlns:dot1x="urn:ieee:std:802.1X:yang:ieee802-dot1x">
            <dot1x:name>{dot1x_name}</dot1x:name>
            <dot1x:system-access-control>{enabled}</dot1x:system-access-control>
         </dot1x:pae-system>
         </sys:system>
      </config>
   </edit-config>
   </rpc>""",
    
}
 
    
RPC_REGISTRY = {
    RPC_ID.WATCHDOG:{
        "name":"Watchdog Reset",
        "rpc" : RPC_SENDS["watchdog"],
    },
    
    RPC_ID.CREATE_SUBSCRIPTION:{
        "name" : "Subscribe To ALL Notifications",
        "rpc" : RPC_SENDS["create_subscription"] 
        },
    
    RPC_ID.CALL_HOME:{
        },
    
    RPC_ID.USER:{
        },
    
    RPC_ID.CERT_TO_NAME:{
        },
    
    RPC_ID.IEEE_8021X:{
        "name":"IEEE 8021x Enable_Disable",
        "rpc" : [{
            "template" : RPC_SENDS["ietf_interface_config"],
            "inputs" : ["interface_name",
                        "pae_system",
                        "held_period",
                        "max_retry", 
                        "iana_interface_type"
                        ]
            
          
          },
          
          {
                 "template" :  RPC_SENDS["ietf_system_config"],
                 "inputs" : ["dot1x_name","enabled"]
          }
          ]
        },
    
    RPC_ID.FTPES:{
        },
   
}


#                              "system_config" : ["dot1x_name","enabled"]}]

to_send = []


def configure_rpc(rpc_id):
  rpc_group = RPC_REGISTRY[rpc_id]["rpc"]
  for rpc in rpc_group:
    rpc_template = rpc["template"]
    rpc_inputs = rpc["inputs"] 
    print(f"\n TEMPLATE: {rpc_template}")
    
    
    print(f"PARAMETERS: ")
    for paramter in rpc_inputs:
      print(paramter)
      
    
    
  
  
  
    


configure_rpc(RPC_ID.IEEE_8021X)
