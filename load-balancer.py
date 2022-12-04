import subprocess
import argparse
from scapy.all import *
from time import sleep

OK = 0
TUN_DNAT_CHAIN = "tun_dnat"

class LoadBalancer:
    def __init__(self, hst_ip: str, homea_ips: list[str]) -> None:
        self.DNAT_TUN = "ip6tables -t nat -A tun_dnat -p ipv6 -s {source} -d {host_ip} -j DNAT --to-destination {ha_ip}"
        self.counter = 0
        self.host_ip = hst_ip
        self.ha_ips = homea_ips


    def main_loop(self) -> None:
        def packet_handler(packet):
            if MIP6MH_BA in packet and packet["MIP6MH_BA"].status == OK and packet["IPv6"].src != self.host_ip:
                addr = packet["IPv6"].src
                source = packet["IPv6"].dst
                nat_p = packet["IPv6"].copy()
                nat_p["IPv6"].src = self.host_ip
                send(nat_p)
                subprocess.run(self.DNAT_TUN.format(source=source ,host_ip=self.host_ip, ha_ip=addr).split())
            if MIP6MH_BU in packet and packet["IPv6"].dst == self.host_ip:
                nat_p = packet["IPv6"].copy()
                nat_p["IPv6"].dst = self.ha_ips[self.counter % len(self.ha_ips)]
                send(nat_p)
                self.counter += 1

        ifaces = [iface.name for iface in get_working_ifaces()]
        sniffer = AsyncSniffer(
            iface=ifaces,
            filter="ip6 proto 135",
            prn=packet_handler
        )
        sniffer.start()

        print("LoadBalancer ready.")
        try:
            while True:
                sleep(0.5)
        except KeyboardInterrupt:
            sniffer.stop()
            sniffer.join()
            #cleanup jobs
            self.cleanup()
            print("LoadBalancer successfully unloaded all configurations.")

    def init(self) -> None:
        subprocess.run(f"ip6tables -t nat -N {TUN_DNAT_CHAIN}".split())
        subprocess.run(f"ip6tables -t nat -I PREROUTING -j {TUN_DNAT_CHAIN}".split())

    def cleanup(self) -> None:
        subprocess.run(f"ip6tables -t nat -D PREROUTING -j {TUN_DNAT_CHAIN}".split())
        subprocess.run(f"ip6tables -t nat -F {TUN_DNAT_CHAIN}".split())
        subprocess.run(f"ip6tables -t nat -X {TUN_DNAT_CHAIN}".split())


def main(host_ip, ips):
    lb = LoadBalancer(host_ip, ips)

    lb.init()
    try:
        lb.main_loop()
    except:
        lb.cleanup()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="LoadBalance for given ips on the given host ip")
    parser.add_argument("ips", help="ips to loadbalance between", nargs="+")
    parser.add_argument("--host", help="host ip")
    args = parser.parse_args()

    print(args.ips)
    print(args.host)

    main(args.host, args.ips)