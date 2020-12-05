__author__ = ["Manav Vagrecha", "Shreyansh Shah", "Devam Shah"]
__email__ = ["manavkumar.v@ahduni.edu.in", "shreyansh.s1@ahduni.edu.in", "devam.s1@ahduni.edu.in"]


import ipaddress
import logging
import socket
from urllib.parse import urlparse

import requests
from message_d.message import (UdpTrackerAnnounce, UdpTrackerAnnounceOutput, UdpTrackerConnection)
from peers_d import peers_manager
import tracker_d.socket_address as socket_address

class UdpScrapper(object):

    def __init__(self, torrent, announce, dict_sock_addr):
        self.torrent = torrent
        parsed = urlparse(announce)
        self.dict_sock_addr = dict_sock_addr
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.settimeout(4)
        ip, port = socket.gethostbyname(parsed.hostname), parsed.port

        if ipaddress.ip_address(ip).is_private:
            return

        tracker_connection_input = UdpTrackerConnection()
        response = self.send_message((ip, port), sock, tracker_connection_input)

        if not response:
            raise Exception("\033[95m [?] No response for UdpTrackerConnection\033[00m")

        tracker_connection_output = UdpTrackerConnection()
        tracker_connection_output.from_bytes(response)

        tracker_announce_input = UdpTrackerAnnounce(self.torrent.info_hash, tracker_connection_output.conn_id,
                                                    self.torrent.peer_id)
        response = self.send_message((ip, port), sock, tracker_announce_input)

        if not response:
            raise Exception("\033[95m [?] No response for UdpTrackerAnnounce\033[00m")

        tracker_announce_output = UdpTrackerAnnounceOutput()
        tracker_announce_output.from_bytes(response)

        for ip, port in tracker_announce_output.list_sock_addr:
            sock_addr = socket_address.SockAddr(ip, port)

            if sock_addr.__hash__() not in self.dict_sock_addr:
                self.dict_sock_addr[sock_addr.__hash__()] = sock_addr

        print("\033[95m [>] Got \033[00m%d\033[95m peers\033[00m" % len(self.dict_sock_addr))
        
    def get_dict_sock_addr(self):
        return self.dict_sock_addr

    def send_message(self, conn, sock, tracker_message):
        message = tracker_message.to_bytes()
        trans_id = tracker_message.trans_id
        action = tracker_message.action
        size = len(message)

        sock.sendto(message, conn)

        try:
            response = peers_manager.PeersManager._read_from_socket(sock)
        except socket.timeout as e:
            logging.debug("\033[91m [!] Timeout : \033[00m%s" % e)
            return
        except Exception as e:
            print("\033[91m [!] Error : Message was not sent successfully : \033[00m%s" % e.__str__())
            return

        if len(response) < size:
            print("\033[91m [!] Error : Did not get full message.\033[00m")

        if action != response[0:4] or trans_id != response[4:8]:
            print("\033[91m [!] Transaction-ID did not match\033[00m")

        return response
