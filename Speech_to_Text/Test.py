import snap7

def main():
    plc_ip= "192.168.0.1"
    plc_rack = 0
    plc_slot = 2
    plc_port = 10999

    try: 
        client= snap7.client.Client()
        client.connect(plc_ip,plc_rack,plc_rack,plc_port)
        print("Connected to PLC")

    except Exception as e:
        print("Error")

if __name__ == 'main':
    main() 