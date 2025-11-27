import board
import busio
import time
import adafruit_espatcontrol

# === CONFIG ===
UART_TX = board.GP0
UART_RX = board.GP1
BAUD_RATE = 115200
AP_CHANNEL = 6
AP_ENCRYPTION = 3  # 0=open, 1=WEP, 2=WPA_PSK, 3=WPA2_PSK, 4=WPA_WPA2_PSK

esp = None

def startWiFi():
    global esp
    # Get wifi details and more from a secrets.py file
    try:
        from secrets import secrets
    except ImportError:
        print("WiFi secrets are kept in secrets.py, please add them there!")
        raise

    # === UART ===
    uart = busio.UART(tx=UART_TX, rx=UART_RX, baudrate=BAUD_RATE)

    # === ESP ===
    esp = adafruit_espatcontrol.ESP_ATcontrol(uart, default_baudrate=BAUD_RATE)

    # === INIT ===
    print("Resetting ESP module")
    esp.soft_reset()
    print("Setting up access point")
    time.sleep(3)
    send_cmd("AT")
    send_cmd("AT+CWMODE=2")
    send_cmd("AT+RST", timeout=5)
    send_cmd("ATE0")  # Disable echo
    time.sleep(5)
    send_cmd("AT")
    send_cmd(f'AT+CWSAP="{secrets["ssid"]}","{secrets["password"]}",{AP_CHANNEL},{AP_ENCRYPTION}')
    send_cmd("AT+CIPMUX=1")
    send_cmd("AT+CIPSERVER=1,80")

    print(f"\nAP READY: {secrets["ssid"]} @ {BAUD_RATE} baud")
    print("Visit: http://192.168.4.1")

# === SEND COMMAND ===
def send_cmd(cmd, timeout=5):
    print(f"> {cmd}")
    try:
        return esp.at_response(cmd, timeout=timeout)
    except Exception as e:
        print(f"ERROR: {e}")
        raise