#!/usr/bin/env python3
"""
ZeroLinkChain VPN Protocol - Custom VPN Application
TCP/UDP support, not web-based, standalone application
Domain: zerolinkchain.com
"""

import socket
import struct
import threading
import time
import random
import json
import hashlib
import base64
import os
import sys
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
import select

# VPN Protocol Constants
VPN_MAGIC = 0x5A45524F  # "ZERO" in hex
VPN_VERSION = 1
VPN_PORT = 9999

# Packet Types
class PacketType:
    HANDSHAKE = 0x01
    AUTH = 0x02
    DATA = 0x03
    ROUTE_REQUEST = 0x04
    ROUTE_RESPONSE = 0x05
    HEARTBEAT = 0x06
    BANDWIDTH_TEST = 0x07
    DISCONNECT = 0x08
    HOST_DISCOVERY = 0x09
    DEAD_TX = 0x0A

@dataclass
class VPNPacket:
    """VPN protocol packet structure"""
    magic: int = VPN_MAGIC
    version: int = VPN_VERSION
    packet_type: int = 0
    flags: int = 0
    sequence: int = 0
    session_id: int = 0
    payload_length: int = 0
    payload: bytes = b''
    
    def pack(self) -> bytes:
        """Pack packet into bytes"""
        header = struct.pack('!IBBHHII', 
                           self.magic,
                           self.version,
                           self.packet_type,
                           self.flags,
                           self.sequence,
                           self.session_id,
                           self.payload_length)
        return header + self.payload
    
    @classmethod
    def unpack(cls, data: bytes) -> 'VPNPacket':
        """Unpack bytes into packet"""
        if len(data) < 16:  # Header size
            raise ValueError("Packet too small")
        
        header = struct.unpack('!IBBHHII', data[:16])
        packet = cls(
            magic=header[0],
            version=header[1],
            packet_type=header[2],
            flags=header[3],
            sequence=header[4],
            session_id=header[5],
            payload_length=header[6]
        )
        
        if packet.magic != VPN_MAGIC:
            raise ValueError("Invalid magic number")
        
        if len(data) >= 16 + packet.payload_length:
            packet.payload = data[16:16 + packet.payload_length]
        
        return packet

@dataclass
class VPNHost:
    """VPN host information"""
    host_id: str
    ip_address: str
    port: int
    host_type: int  # 1=Found by chain, 2=Joined for rewards, 3=Donated
    connection_type: str  # '4g_5g', 'vps', 'proxy'
    bandwidth_mbps: float
    asn: str
    isp: str
    location: str
    active: bool
    reliability_score: float
    last_seen: float

@dataclass
class VPNRoute:
    """VPN route with multiple hops"""
    route_id: str
    hops: List[VPNHost]
    total_bandwidth: float
    total_latency: float
    hop_count: int
    asn_diversity: List[str]
    isp_diversity: List[str]
    active: bool

class ZeroLinkChainVPN:
        """ZeroLinkChain Custom VPN Protocol Implementation

        Confidential multi-hop routing additions:
        - Enforce minimum of 3 hops (entry, at least one middle, exit)
        - First and last hop must be "confidential capable" (high reliability & bandwidth)
        - Simple local payload encryption using wallet private key material (XOR stream derived
            from SHA256(private_key || route_id)). This is a lightweight placeholder until full
            PGP hybrid encryption (sign + encrypt with per-hop public keys) is integrated.
        """
    
    def __init__(self, mode: str = "client", host: str = "127.0.0.1", port: int = VPN_PORT):
        self.mode = mode  # "client" or "server"
        self.host = host
        self.port = port
        self.running = False
        self.connections = {}
        self.routes = []
        self.hosts = []
        self.session_id = random.randint(1000, 9999)
        self.sequence = 0
    self.enable_confidential_routes = True
    self.wallet_private_key = os.environ.get("ZLC_WALLET_PRIVKEY", "demo_wallet_privkey")
        
        # Protocol support
        self.supports_tcp = True
        self.supports_udp = True
        
        # Load hosts from blockchain
        self.load_hosts_from_blockchain()
    
    def load_hosts_from_blockchain(self):
        """Load VPN hosts from ZeroLinkChain blockchain"""
        try:
            from zerolinkchain_core import get_core
            core = get_core()
            
            for host_data in core.hosts:
                if host_data.active:
                    host = VPNHost(
                        host_id=host_data.host_id,
                        ip_address=host_data.ip_address,
                        port=host_data.port,
                        host_type=host_data.host_type,
                        connection_type=host_data.connection_type,
                        bandwidth_mbps=host_data.bandwidth_mbps,
                        asn=host_data.asn,
                        isp=host_data.isp,
                        location=host_data.location,
                        active=host_data.active,
                        reliability_score=host_data.reliability_score,
                        last_seen=host_data.last_seen
                    )
                    self.hosts.append(host)
            
            print(f"📡 Loaded {len(self.hosts)} VPN hosts from blockchain")
            
        except Exception as e:
            print(f"⚠️  Could not load hosts from blockchain: {e}")
            self.load_default_hosts()
    
    def load_default_hosts(self):
        """Load default VPN hosts for testing"""
        default_hosts = [
            {
                "host_id": "default_host_001",
                "ip_address": "185.230.223.45",
                "port": 9999,
                "host_type": 1,
                "connection_type": "vps",
                "bandwidth_mbps": 1000.0,
                "asn": "AS16276",
                "isp": "OVH",
                "location": "Netherlands",
                "reliability_score": 0.9
            },
            {
                "host_id": "default_host_002",
                "ip_address": "89.187.162.89",
                "port": 9999,
                "host_type": 2,
                "connection_type": "proxy",
                "bandwidth_mbps": 500.0,
                "asn": "AS3320",
                "isp": "Deutsche Telekom",
                "location": "Germany",
                "reliability_score": 0.85
            }
        ]
        
        for host_data in default_hosts:
            host = VPNHost(
                host_id=host_data["host_id"],
                ip_address=host_data["ip_address"],
                port=host_data["port"],
                host_type=host_data["host_type"],
                connection_type=host_data["connection_type"],
                bandwidth_mbps=host_data["bandwidth_mbps"],
                asn=host_data["asn"],
                isp=host_data["isp"],
                location=host_data["location"],
                active=True,
                reliability_score=host_data["reliability_score"],
                last_seen=time.time()
            )
            self.hosts.append(host)
    
    def create_optimal_route(self, destination: str = None, min_hops: int = 3, max_hops: int = 5) -> VPNRoute:
        """Create optimal VPN route with ASN/ISP diversity and confidential entry/exit hops.

        Confidential capability heuristic (temporary):
        - reliability_score >= 0.8
        - bandwidth_mbps >= 100
        These hosts are eligible to serve as first/last hop when confidential routing is enabled.
        """
        if min_hops < 3:
            min_hops = 3  # Enforce at least 3 hops as per design
        active_hosts = [h for h in self.hosts if h.active]
        if len(active_hosts) < min_hops:
            raise Exception(f"Not enough active hosts for routing ({len(active_hosts)} < {min_hops})")

        confidential_candidates = [h for h in active_hosts if h.reliability_score >= 0.8 and h.bandwidth_mbps >= 100]
        if self.enable_confidential_routes and len(confidential_candidates) < 2:
            raise Exception("Insufficient confidential-capable hosts for entry/exit")

        # Sort by combined score
        sorted_hosts = sorted(active_hosts, key=lambda h: h.reliability_score * h.bandwidth_mbps, reverse=True)

        selected_hosts = []
        used_asns = set()
        used_isps = set()

        # Pick confidential entry
        if self.enable_confidential_routes:
            entry = sorted(confidential_candidates, key=lambda h: h.reliability_score * h.bandwidth_mbps, reverse=True)[0]
            selected_hosts.append(entry)
            used_asns.add(entry.asn)
            used_isps.add(entry.isp)

        # Fill middle hops maintaining diversity
        for host in sorted_hosts:
            if len(selected_hosts) >= max_hops - 1:  # leave room for exit
                break
            if host in selected_hosts:
                continue
            if host.asn in used_asns or host.isp in used_isps:
                continue
            selected_hosts.append(host)
            used_asns.add(host.asn)
            used_isps.add(host.isp)

        # Ensure minimum hops by relaxing diversity if needed
        if len(selected_hosts) < (min_hops - 1):  # minus one for exit
            for host in sorted_hosts:
                if len(selected_hosts) >= (min_hops - 1):
                    break
                if host not in selected_hosts:
                    selected_hosts.append(host)

        # Pick confidential exit (different from entry)
        if self.enable_confidential_routes:
            exit_candidates = [h for h in confidential_candidates if h not in selected_hosts or h == selected_hosts[0]]
            # Prefer a different host; if only one candidate, reuse (logged)
            exit_host = None
            for h in exit_candidates:
                if h is not selected_hosts[0]:
                    exit_host = h
                    break
            if not exit_host:
                exit_host = exit_candidates[0]  # fallback
            if exit_host not in selected_hosts:
                selected_hosts.append(exit_host)
        
        # Guarantee hop count
        if len(selected_hosts) < min_hops:
            # add more hosts ignoring diversity
            for host in sorted_hosts:
                if len(selected_hosts) >= min_hops:
                    break
                if host not in selected_hosts:
                    selected_hosts.append(host)
        
        route = VPNRoute(
            route_id=f"route_{int(time.time())}_{random.randint(1000, 9999)}",
            hops=selected_hosts,
            total_bandwidth=min([h.bandwidth_mbps for h in selected_hosts]),
            total_latency=sum([random.randint(10, 50) for _ in selected_hosts]),
            hop_count=len(selected_hosts),
            asn_diversity=list(used_asns),
            isp_diversity=list(used_isps),
            active=True
        )
        
        self.routes.append(route)
        print(f"🛣️  Created VPN route: {route.route_id}")
        print(f"   Hops: {route.hop_count}")
        print(f"   ASN Diversity: {route.asn_diversity}")
        print(f"   ISP Diversity: {route.isp_diversity}")
        print(f"   Bandwidth: {route.total_bandwidth} Mbps")
        
        return route

    # --- Confidential encryption helpers -------------------------------------------------
    def _derive_stream_key(self, route: VPNRoute) -> bytes:
        material = (self.wallet_private_key + route.route_id).encode()
        return hashlib.sha256(material).digest()

    def encrypt_payload(self, data: bytes, route: VPNRoute) -> bytes:
        key = self._derive_stream_key(route)
        return bytes(b ^ key[i % len(key)] for i, b in enumerate(data))

    def decrypt_payload(self, data: bytes, route: VPNRoute) -> bytes:
        # XOR symmetric
        return self.encrypt_payload(data, route)

    # --------------------------------------------------------------------------------------
    
    def start_server(self):
        """Start VPN server (TCP and UDP)"""
        if self.mode != "server":
            print("❌ Not in server mode")
            return
        
        self.running = True
        
        # Start TCP server
        tcp_thread = threading.Thread(target=self._tcp_server)
        tcp_thread.daemon = True
        tcp_thread.start()
        
        # Start UDP server
        udp_thread = threading.Thread(target=self._udp_server)
        udp_thread.daemon = True
        udp_thread.start()
        
        print(f"🚀 ZeroLinkChain VPN Server started on {self.host}:{self.port}")
        print(f"✅ TCP Support: {self.supports_tcp}")
        print(f"✅ UDP Support: {self.supports_udp}")
        print(f"🌐 Available hosts: {len(self.hosts)}")
    
    def _tcp_server(self):
        """TCP server loop"""
        try:
            server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            server_socket.bind((self.host, self.port))
            server_socket.listen(10)
            
            print(f"📡 TCP server listening on {self.host}:{self.port}")
            
            while self.running:
                try:
                    client_socket, client_addr = server_socket.accept()
                    print(f"🔗 TCP connection from {client_addr}")
                    
                    # Handle client in separate thread
                    client_thread = threading.Thread(
                        target=self._handle_tcp_client,
                        args=(client_socket, client_addr)
                    )
                    client_thread.daemon = True
                    client_thread.start()
                    
                except Exception as e:
                    if self.running:
                        print(f"TCP server error: {e}")
                        
        except Exception as e:
            print(f"❌ TCP server failed to start: {e}")
        finally:
            server_socket.close()
    
    def _udp_server(self):
        """UDP server loop"""
        try:
            server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            server_socket.bind((self.host, self.port + 1))  # UDP on port + 1
            
            print(f"📡 UDP server listening on {self.host}:{self.port + 1}")
            
            while self.running:
                try:
                    data, client_addr = server_socket.recvfrom(4096)
                    print(f"📦 UDP packet from {client_addr}")
                    
                    # Handle UDP packet
                    self._handle_udp_packet(server_socket, data, client_addr)
                    
                except Exception as e:
                    if self.running:
                        print(f"UDP server error: {e}")
                        
        except Exception as e:
            print(f"❌ UDP server failed to start: {e}")
        finally:
            server_socket.close()
    
    def _handle_tcp_client(self, client_socket: socket.socket, client_addr: Tuple):
        """Handle TCP client connection"""
        try:
            while self.running:
                # Receive packet
                data = client_socket.recv(4096)
                if not data:
                    break
                
                try:
                    packet = VPNPacket.unpack(data)
                    response = self._process_packet(packet, client_addr)
                    
                    if response:
                        client_socket.send(response.pack())
                        
                except Exception as e:
                    print(f"Packet processing error: {e}")
                    
        except Exception as e:
            print(f"TCP client error: {e}")
        finally:
            client_socket.close()
            print(f"🔌 TCP connection closed: {client_addr}")
    
    def _handle_udp_packet(self, server_socket: socket.socket, data: bytes, client_addr: Tuple):
        """Handle UDP packet"""
        try:
            packet = VPNPacket.unpack(data)
            response = self._process_packet(packet, client_addr)
            
            if response:
                server_socket.sendto(response.pack(), client_addr)
                
        except Exception as e:
            print(f"UDP packet error: {e}")
    
    def _process_packet(self, packet: VPNPacket, client_addr: Tuple) -> Optional[VPNPacket]:
        """Process VPN packet and return response"""
        if packet.packet_type == PacketType.HANDSHAKE:
            return self._handle_handshake(packet, client_addr)
        elif packet.packet_type == PacketType.AUTH:
            return self._handle_auth(packet, client_addr)
        elif packet.packet_type == PacketType.ROUTE_REQUEST:
            return self._handle_route_request(packet, client_addr)
        elif packet.packet_type == PacketType.BANDWIDTH_TEST:
            return self._handle_bandwidth_test(packet, client_addr)
        elif packet.packet_type == PacketType.HOST_DISCOVERY:
            return self._handle_host_discovery(packet, client_addr)
        elif packet.packet_type == PacketType.DEAD_TX:
            return self._handle_dead_tx(packet, client_addr)
        elif packet.packet_type == PacketType.HEARTBEAT:
            return self._handle_heartbeat(packet, client_addr)
        elif packet.packet_type == PacketType.DATA:
            return self._handle_data(packet, client_addr)
        else:
            print(f"❓ Unknown packet type: {packet.packet_type}")
            return None
    
    def _handle_handshake(self, packet: VPNPacket, client_addr: Tuple) -> VPNPacket:
        """Handle handshake packet"""
        print(f"🤝 Handshake from {client_addr}")
        
        response_data = {
            "status": "ok",
            "server": "ZeroLinkChain VPN",
            "version": VPN_VERSION,
            "supports_tcp": True,
            "supports_udp": True,
            "available_hosts": len([h for h in self.hosts if h.active])
        }
        
        response = VPNPacket(
            packet_type=PacketType.HANDSHAKE,
            session_id=packet.session_id,
            sequence=packet.sequence + 1,
            payload=json.dumps(response_data).encode()
        )
        response.payload_length = len(response.payload)
        
        return response
    
    def _handle_auth(self, packet: VPNPacket, client_addr: Tuple) -> VPNPacket:
        """Handle authentication packet"""
        print(f"🔐 Auth from {client_addr}")
        
        # Simple auth for demo (in production, use proper crypto)
        response_data = {
            "status": "authenticated",
            "session_id": packet.session_id,
            "permissions": ["route", "host_discovery", "dead_tx"]
        }
        
        response = VPNPacket(
            packet_type=PacketType.AUTH,
            session_id=packet.session_id,
            sequence=packet.sequence + 1,
            payload=json.dumps(response_data).encode()
        )
        response.payload_length = len(response.payload)
        
        return response
    
    def _handle_route_request(self, packet: VPNPacket, client_addr: Tuple) -> VPNPacket:
        """Handle route request packet"""
        print(f"🛣️  Route request from {client_addr}")
        
        try:
            request_data = json.loads(packet.payload.decode())
            min_hops = request_data.get("min_hops", 3)
            max_hops = request_data.get("max_hops", 5)
            
            route = self.create_optimal_route(min_hops=min_hops, max_hops=max_hops)
            
            response_data = {
                "status": "route_created",
                "route_id": route.route_id,
                "hop_count": route.hop_count,
                "confidential": self.enable_confidential_routes,
                "entry_host": route.hops[0].host_id if route.hops else None,
                "exit_host": route.hops[-1].host_id if route.hops else None,
                "hops": [
                    {
                        "host_id": hop.host_id,
                        "ip_address": hop.ip_address,
                        "port": hop.port,
                        "location": hop.location,
                        "asn": hop.asn,
                        "isp": hop.isp
                    } for hop in route.hops
                ],
                "total_bandwidth": route.total_bandwidth,
                "total_latency": route.total_latency,
                "asn_diversity": route.asn_diversity,
                "isp_diversity": route.isp_diversity
            }
            
        except Exception as e:
            response_data = {
                "status": "error",
                "message": str(e)
            }
        
        response = VPNPacket(
            packet_type=PacketType.ROUTE_RESPONSE,
            session_id=packet.session_id,
            sequence=packet.sequence + 1,
            payload=json.dumps(response_data).encode()
        )
        response.payload_length = len(response.payload)
        
        return response

    def _handle_data(self, packet: VPNPacket, client_addr: Tuple) -> VPNPacket:
        """Handle encrypted data packet (placeholder – multi-hop forwarding TBD)."""
        try:
            payload_obj = json.loads(packet.payload.decode())
            route_id = payload_obj.get("route_id")
            encrypted_b64 = payload_obj.get("data")
            if not route_id or not encrypted_b64:
                raise ValueError("Missing route_id or data")
            # Locate route
            route = next((r for r in self.routes if r.route_id == route_id and r.active), None)
            if not route:
                raise ValueError("Route not found or inactive")
            encrypted = base64.b64decode(encrypted_b64)
            plaintext = self.decrypt_payload(encrypted, route)
            # For now we just acknowledge; forwarding chain is TODO
            response_payload = {
                "status": "received",
                "route_id": route_id,
                "decrypted_len": len(plaintext),
                "forwarded": False,
                "todo": "Implement multi-hop forwarding in C layer or async dispatcher"
            }
        except Exception as e:
            response_payload = {"status": "error", "message": str(e)}

        resp = VPNPacket(
            packet_type=PacketType.DATA,
            session_id=packet.session_id,
            sequence=packet.sequence + 1,
            payload=json.dumps(response_payload).encode()
        )
        resp.payload_length = len(resp.payload)
        return resp
    
    def _handle_bandwidth_test(self, packet: VPNPacket, client_addr: Tuple) -> VPNPacket:
        """Handle bandwidth test packet"""
        print(f"📊 Bandwidth test from {client_addr}")
        
        # Echo back the same data for bandwidth testing
        response = VPNPacket(
            packet_type=PacketType.BANDWIDTH_TEST,
            session_id=packet.session_id,
            sequence=packet.sequence + 1,
            payload=packet.payload  # Echo back
        )
        response.payload_length = len(response.payload)
        
        return response
    
    def _handle_host_discovery(self, packet: VPNPacket, client_addr: Tuple) -> VPNPacket:
        """Handle host discovery packet"""
        print(f"🔍 Host discovery from {client_addr}")
        
        active_hosts = [h for h in self.hosts if h.active]
        
        response_data = {
            "status": "hosts_found",
            "total_hosts": len(active_hosts),
            "hosts": [
                {
                    "host_id": host.host_id,
                    "host_type": host.host_type,
                    "location": host.location,
                    "bandwidth_mbps": host.bandwidth_mbps,
                    "reliability_score": host.reliability_score,
                    "connection_type": host.connection_type,
                    "asn": host.asn,
                    "isp": host.isp
                } for host in active_hosts[:20]  # Limit to 20 hosts
            ]
        }
        
        response = VPNPacket(
            packet_type=PacketType.HOST_DISCOVERY,
            session_id=packet.session_id,
            sequence=packet.sequence + 1,
            payload=json.dumps(response_data).encode()
        )
        response.payload_length = len(response.payload)
        
        return response
    
    def _handle_dead_tx(self, packet: VPNPacket, client_addr: Tuple) -> VPNPacket:
        """Handle dead transaction packet"""
        print(f"💀 Dead TX from {client_addr}")
        
        try:
            # Forward dead TX to blockchain
            from zerolinkchain_core import get_core
            core = get_core()
            
            dead_tx_data = json.loads(packet.payload.decode())
            
            if dead_tx_data.get("type") == "chainchat":
                tx_id = core.send_chainchat_message(
                    dead_tx_data.get("sender", "anonymous"),
                    dead_tx_data.get("recipient", "public"),
                    dead_tx_data.get("message", ""),
                    dead_tx_data.get("is_video", False)
                )
                response_data = {"status": "dead_tx_created", "tx_id": tx_id}
                
            elif dead_tx_data.get("type") == "chainstore":
                file_data = base64.b64decode(dead_tx_data.get("file_data", ""))
                tx_id = core.store_chainstore_file(
                    dead_tx_data.get("filename", "unknown.dat"),
                    file_data,
                    dead_tx_data.get("uploader", "anonymous"),
                    dead_tx_data.get("pgp_key", "default_key")
                )
                response_data = {"status": "dead_tx_created", "tx_id": tx_id}
                
            else:
                response_data = {"status": "error", "message": "Unknown dead TX type"}
                
        except Exception as e:
            response_data = {"status": "error", "message": str(e)}
        
        response = VPNPacket(
            packet_type=PacketType.DEAD_TX,
            session_id=packet.session_id,
            sequence=packet.sequence + 1,
            payload=json.dumps(response_data).encode()
        )
        response.payload_length = len(response.payload)
        
        return response
    
    def _handle_heartbeat(self, packet: VPNPacket, client_addr: Tuple) -> VPNPacket:
        """Handle heartbeat packet"""
        # Simple heartbeat response
        response = VPNPacket(
            packet_type=PacketType.HEARTBEAT,
            session_id=packet.session_id,
            sequence=packet.sequence + 1,
            payload=b"alive"
        )
        response.payload_length = len(response.payload)
        
        return response
    
    def connect_to_host(self, host_ip: str, host_port: int, protocol: str = "tcp") -> bool:
        """Connect to VPN host"""
        if self.mode != "client":
            print("❌ Not in client mode")
            return False
        
        try:
            if protocol.lower() == "tcp":
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.connect((host_ip, host_port))
            else:  # UDP
                sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            
            # Send handshake
            handshake = VPNPacket(
                packet_type=PacketType.HANDSHAKE,
                session_id=self.session_id,
                sequence=self.sequence,
                payload=b"ZeroLinkChain VPN Client"
            )
            handshake.payload_length = len(handshake.payload)
            
            if protocol.lower() == "tcp":
                sock.send(handshake.pack())
                response_data = sock.recv(4096)
            else:
                sock.sendto(handshake.pack(), (host_ip, host_port))
                response_data, _ = sock.recvfrom(4096)
            
            response = VPNPacket.unpack(response_data)
            
            if response.packet_type == PacketType.HANDSHAKE:
                print(f"✅ Connected to {host_ip}:{host_port} via {protocol.upper()}")
                return True
            
        except Exception as e:
            print(f"❌ Connection failed: {e}")
        
        return False
    
    def stop(self):
        """Stop VPN server/client"""
        self.running = False
        print("🛑 ZeroLinkChain VPN stopped")

def main():
    """Main VPN application"""
    if len(sys.argv) < 2:
        print("ZeroLinkChain VPN Protocol - Custom VPN Application")
        print("Usage:")
        print("  python3 zerolinkchain_vpn.py server [host] [port]")
        print("  python3 zerolinkchain_vpn.py client [target_host] [target_port]")
        print("")
        print("Features:")
        print("  ✅ TCP/UDP Support")
        print("  ✅ Custom Protocol (not OpenVPN)")
        print("  ✅ ASN/ISP Diversity Routing")
        print("  ✅ Dead TX Support")
        print("  ✅ Blockchain Integration")
        print("  ✅ Host Discovery")
        print("  ✅ Bandwidth Testing")
        return
    
    mode = sys.argv[1].lower()
    
    if mode == "server":
        host = sys.argv[2] if len(sys.argv) > 2 else "0.0.0.0"
        port = int(sys.argv[3]) if len(sys.argv) > 3 else VPN_PORT
        
        vpn = ZeroLinkChainVPN(mode="server", host=host, port=port)
        vpn.start_server()
        
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            vpn.stop()
    
    elif mode == "client":
        target_host = sys.argv[2] if len(sys.argv) > 2 else "127.0.0.1"
        target_port = int(sys.argv[3]) if len(sys.argv) > 3 else VPN_PORT
        
        vpn = ZeroLinkChainVPN(mode="client")
        
        print(f"🔗 Connecting to {target_host}:{target_port}")
        
        # Test TCP connection
        if vpn.connect_to_host(target_host, target_port, "tcp"):
            print("✅ TCP connection successful")
        else:
            print("❌ TCP connection failed")
        
        # Test UDP connection
        if vpn.connect_to_host(target_host, target_port + 1, "udp"):
            print("✅ UDP connection successful")
        else:
            print("❌ UDP connection failed")
    
    else:
        print("❌ Invalid mode. Use 'server' or 'client'")

if __name__ == "__main__":
    main()
