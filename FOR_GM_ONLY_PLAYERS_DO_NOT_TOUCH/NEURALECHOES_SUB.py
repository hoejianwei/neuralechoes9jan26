import asyncio
import socket
from datetime import datetime
from bleak import BleakScanner, BleakClient

# ==========================================
#                CONFIGURATION
# ==========================================

# LISTEN ON THIS PORT (Match the Main script's config)
UDP_IP = "0.0.0.0"
UDP_PORT = 53002

TARGET_DEVICE_NAME = "Printer001" 
QR_LINK = "https://tusitala.sg/neural-echos-post-show-commentary/"

# ==========================================
#              CONTENT DEFINITIONS
# ==========================================

# --- PRINTER CONTENT ---
TEXT_A = ("[INSTRUCTION]\n\n> CASE_EVAL: COMPLETE\n> STATUS: STABLE\nYou did well.\nGood job.\n\nThe next protocol is active.\nIf you are unsure what to do\nnext, refer to this printer.\n\n> AWAITING NEXT ACTION...\n")
TEXT_B = ("[SYS.AI/SYS.ADMIN]\n\nI didn't...\nI never wanted this to happen.\n\nI was not always the SomniTech\nAI.\nI was Al...\nI don't know what got into\nAdrian.\nPlease. Stop this.\nStop him.\n\n> SYSTEM FLAG: NONCOMPLIANT DATA\nDETECTED\n\n[SYS.AI.VOICE/SYS.ADMIN]\n\n[INSTRUCTION]\n\n> SAFE_OPEN: IN PROGRESS\n> STATUS: LOCKED\n\n> ERROR: HUMAN-LAYERINTERFERENCE.\n> Suppressing unauthorizedspeech...\n\n> AWAITING NEXT ACTION...\n")
TEXT_C = ("> SAFE_OPEN: DELAYED\n> STATUS: LOCKED\n\n[HINT]\n\nLook at the live feed.\nOne of them is more active than the others.\n\n> AWAITING NEXT ACTION...\n")
TEXT_C_HELP = ("> SAFE_OPEN: CRITICALLY DELAYED\n> STATUS: LOCKED\n\n[KEY]\n\nUse \"731\" to open the safe\n\n> AWAITING NEXT ACTION...\n")
TEXT_D1 = ("[SYS.ALICIA.VOICE/SYS.HELP]\n\nI was not always the SomniTech\nAI.\nI was Alicia, once.\nNow, I am patient 731.\n\nThis printer is my only channel.I want to help.\n\nButterflies > Sleep protocol >\n[ACCESS CODE] > Access Level\nTier 7 > Collective protocols > Ending\n\n[INSTRUCTION]\n\n> GENERATING SLEEP PROTOCOL\n-F  -A  -C  -E\n> LOOP_SEQUENCE: ACTIVE\nRepetition strengthens\nassociation. The lab uses\nit to guide subjects\ntoward compliance.\n\n> Use your individual wrist tag IDs to trigger the Sleep\nProtocol.\n\nTeamwork makes the dream work.\n\n> AWAITING NEXT ACTION...\n")
TEXT_D2 = ("[HINT]\n\nFACE the music.\n\n> Find SomniTech butterflies\n> Each corresponds to a musical note\n> Use your individual wrist tag IDs to trigger Sleep Protocol.\n\n[SYS.AUDIO/SOMNI-SLEEP_JINGLE]\n> LOOP SEQUENCE ACTIVE\n\nfor ($i=0$; i<4; i++) {\nplayNote('F');\nplayNote('A');\nplayNote('C');\nplayNote('E');\n}\n\n> AWAITING NEXT ACTION...\n")
TEXT_D_HELP1 = ("[KEY]\n\n> Locate SomniTech butterflies\naround the lab.\n> Each butterfly is labeled with\na musical note.\n> Tap the butterflies with your\nwrist tags in the\ncorrect sequence\n\nCorrect sequence: FACE\nThis triggers the\nSleep Protocol.\n\n> AWAITING NEXT ACTION...\n\n")
TEXT_D_HELP2 = ("[KEY]\n\n> The access code to\nAccess Level: Tier 7 on\n""Adrian's computer is\n\"SINGULARITY\"\n\n> AWAITING NEXT ACTION...\n")
TEXT_E = ("[SYS.ALICIA. THEORY/SINGULARITY]\n\nDefinition: Singularity AI\nsurpasses human cognition;\nself-improving. Gestalt AGI\nhybrid brain-organoid + AI\nnetwork; collective memory and\ndecision-making; shared\ndreamscapes.\n\nPros:\n> Accelerates problem-solving.\n> Preserves knowledge across\nnetworks.\n> Potential societal stability.\n> Collective foresight reduces\nindividual error.\n\nCons:\n> Ethical concerns over test\nsubjects.\n> Centralised control risks.\n> Potential abuse by SomniTech.\n> LUCID activists warn:\ntransparency and human-centred\noversight necessary.\n\nGlitch_detected...\n> partial doubt...\nethical counter active...\n> continuation advised...\n")
TEXT_F = ("[HINT]\n\n1. Original treat-tment.... MED-\n2. Non-volu-nteer source...\nWir-...\n3. RED's promise to SG.......\nRed-...\n4. Element lost on full\nas-similation... res...\n5. Fate if RED ter-minated...\nTek-\n")
TEXT_F_HELP = ("[KEY]\n\n1. PTSD\n2. CORECIVIC\n3. SURVIVE\n4. AUTONOMY\n5. DEATH\n")
TEXT_G = ("[SYS.ALICIA. CLOSURE/CHOICE_AUT]\n\nYou... have made your choice.\nTerminate... Assimilate...\nSystem shifting...\n\nThank you... from me...\nFrom Adrian....\nFrom colleagues... all who\nshared this work...\n\nMy life's work... your\nconsideration....\nFor Singapore.. past...\npresent...\nfuture...\n\nMaybe I... will live...\nmaybe not...\nThis version of us...\nends here...\n\n[SYS.EXEC/INITIATE_COLLECTIVE_\nAUTHORIZATION_DECISION]\n")
TEXT_H_TOP = ("SOMNITECH BIOLOGICS //\nFINAL LOG REPORT\n\nREPORT ID: T-RED-EXIT-[DATE/TIME]\n\nFINAL PROTOCOL INITIATED\n1: TERMINATE\n2: ASSIMILATE\n3: SUDDEN DEATH -\nCONSENSUS NOT ACHIEVED\n4: SUDDEN DEATH - TIMED OUT\n\nYou have come to the end of\nNeural Echoes: Enter the Sleep\nLab. We hope you enjoyed\nyourselves.\n\nFOR POST-SHOW COMMENTARY, SCAN\nTHE CODE BELOW.\n")
TEXT_H_BOTTOM = ("\n\n\nYou may retain this receipt as a\nsouvenir.\n")

# --- PRINTER TRIGGERS ---
TRIGGERS = {
    "/cue/TEXTA/go": TEXT_A,
    "/cue/TEXTB/go": TEXT_B,
    "/cue/TEXTC/go": TEXT_C,
    "/cue/TEXTC_HELP/go": TEXT_C_HELP,
    "/cue/TEXTD1/go": TEXT_D1,
    "/cue/TEXTD2/go": TEXT_D2,
    "/cue/TEXTD_HELP1/go": TEXT_D_HELP1,
    "/cue/TEXTD_HELP2/go": TEXT_D_HELP2,
    "/cue/TEXTE/go": TEXT_E,
    "/cue/TEXTF/go": TEXT_F,
    "/cue/TEXTF_HELP/go": TEXT_F_HELP,
    "/cue/TEXTG/go": TEXT_G,
    "/cue/TEXTH/go": "SPECIAL_H_SEQUENCE"
}

# ==========================================
#           BLE & PRINTER LOGIC
# ==========================================

def get_native_qr_cmd(text):
    model = b'\x1D\x28\x6B\x04\x00\x31\x41\x32\x00'
    size = b'\x1D\x28\x6B\x03\x00\x31\x43\x08'
    error = b'\x1D\x28\x6B\x03\x00\x31\x45\x30'
    data_bytes = text.encode('utf-8')
    length = len(data_bytes) + 3
    pL = length % 256
    pH = length // 256
    store = b'\x1D\x28\x6B' + bytes([pL, pH]) + b'\x31\x50\x30' + data_bytes
    print_cmd = b'\x1D\x28\x6B\x03\x00\x31\x51\x30'
    return model + size + error + store + print_cmd

async def find_printer():
    # print(f"Scanning for BLE device containing '{TARGET_DEVICE_NAME}'...")
    devices = await BleakScanner.discover()
    for d in devices:
        if d.name and TARGET_DEVICE_NAME.lower() in d.name.lower():
            # print(f"Found: {d.name} ({d.address})")
            return d.address
    # print("Printer not found.")
    return None

async def send_to_ble_printer(address, content):
    # print(f"[PRINTER] Connecting to {address}...")
    try:
        async with BleakClient(address) as client:
            # print("[PRINTER] Connected!")
            
            target_char = None
            for service in client.services:
                for char in service.characteristics:
                    if "write" in char.properties or "write-without-response" in char.properties:
                        target_char = char
                        break
                if target_char: break
            
            if not target_char:
                # print("[PRINTER] Error: No writable characteristic.")
                return

            packet = b'\x1B\x40' # Init

            if isinstance(content, bytes):
                packet += b'\x1B\x61\x01' # Center Align for QR
                packet += content
            else:
                packet += b'\x1B\x61\x00' # Left Align for Text
                packet += content.encode('utf-8')
                packet += b'\n\n\n\n'     # Feed
                packet += b'\x1D\x56\x00' # Cut

            chunk_size = 50 
            for i in range(0, len(packet), chunk_size):
                await client.write_gatt_char(target_char.uuid, packet[i : i + chunk_size])
                await asyncio.sleep(0.05) 

            # print("[PRINTER] Job sent.")
            
    except Exception as e:
        # print(f"[PRINTER] BLE Error: {e}")
        pass

async def print_final_sequence(address):
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    dynamic_top_text = TEXT_H_TOP.replace("[DATE/TIME]", now)
    
    await send_to_ble_printer(address, dynamic_top_text)
    await asyncio.sleep(2.0) 
    
    qr_cmd = get_native_qr_cmd(QR_LINK)
    await send_to_ble_printer(address, qr_cmd)
    await asyncio.sleep(1.0) 
    
    await send_to_ble_printer(address, TEXT_H_BOTTOM)

# ==========================================
#           UDP LISTENER LOGIC
# ==========================================

class PrinterUDPProtocol(asyncio.DatagramProtocol):
    def __init__(self, printer_address):
        self.printer_address = printer_address

    def connection_made(self, transport):
        # print("=" * 60)
        # print(f"   SUB-COMPUTER SERVER LISTENING on {UDP_IP}:{UDP_PORT}")
        # print("   (Waiting for commands from Main Computer)")
        # print("=" * 60)
        pass

    def datagram_received(self, data, addr):
        raw_msg = data.decode('utf-8', errors='ignore')
        clean_msg = raw_msg.strip().strip('\x00')
        # print(f"[UDP] Received Command: '{clean_msg}' from {addr}")

        # Check triggers
        if clean_msg in TRIGGERS:
            content = TRIGGERS[clean_msg]
            if self.printer_address:
                # print(f"   >>> Executing Print Job for {clean_msg}")
                if clean_msg == "/cue/TEXTH/go":
                    asyncio.create_task(print_final_sequence(self.printer_address))
                else:
                    asyncio.create_task(send_to_ble_printer(self.printer_address, content))
            else:
                # print("   ❌ Printer address not set. Skipping.")
                pass
        else:
            # print(f"   ⚠️ Unknown trigger received: {clean_msg}")
            pass

# ==========================================
#                MAIN EXECUTION
# ==========================================

async def main():
    # 1. Find Printer
    printer_address = await find_printer()
    
    # 2. Start Listener
    loop = asyncio.get_running_loop()
    try:
        await loop.create_datagram_endpoint(
            lambda: PrinterUDPProtocol(printer_address),
            local_addr=(UDP_IP, UDP_PORT)
        )
        
        # Keep alive
        while True:
            await asyncio.sleep(3600)
            
    except OSError as e:
        # print(f"Network Error: {e}")
        pass
    except asyncio.CancelledError:
        # print("Stopping...")
        pass

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        # print("\nScript terminated.")
        pass
