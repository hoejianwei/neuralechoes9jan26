import asyncio
import tinytuya
import threading
import socket
import time
import tkinter as tk  
from datetime import datetime
from bleak import BleakScanner, BleakClient
import subprocess  # Add this at the top of your script
import os

# ==========================================
#                CONFIGURATION
# ==========================================

# --- NETWORK (LISTENER) ---
UDP_IP = "0.0.0.0"
UDP_PORT = 53001          

# --- QLAB RELAY SETTINGS ---
QLAB_IP = "127.0.0.1"      
QLAB_PORT = 53535          

# --- SAFE SETTINGS (SENDING) ---
SAFE_IP = "<broadcast>"   
SAFE_PORT = 4000

# --- SUB COMPUTER (PRINTER PROXY) SETTINGS ---
# UPDATED: Use Broadcast so we don't care what the IP is
SUB_COMPUTER_IP = "<broadcast>" 
SUB_COMPUTER_PORT = 53002

# --- SINGING SEQUENCE SETTINGS ---
# UPDATED: Changed to /go as per your request
SING_SEQUENCE = [
    "/cue/NOTEA/go",   # Step 1
    "/cue/NOTEB/go",   # Step 2
    "/cue/NOTEC/go",   # Step 3
    "/cue/NOTED/go"    # Step 4
]
SING_MAX_GAP = 2.0        
SING_QLAB_CMD = "/cue/SING/go" # UPDATED: Changed to /go
SING_FAIL_CMD = "/cue/FAIL/go"

# --- PRINTER SETTINGS ---
TARGET_DEVICE_NAME = "Printer001" 
QR_LINK = "https://tusitala.sg/neural-echos-post-show-commentary/"

# Add this under the DEVICES_CONFIG or SCENE_DATA section
LIGHT_REPEAT_DELAY = 0.2  # Seconds between the wake-up signal and the confirmation signal

# --- LIGHTS SETTINGS (L1 - L8) ---
DEVICES_CONFIG = {
    "L1": { "id": "a37c400bc9fb08144aaoyw", "ip": "192.168.0.27", "key": "Sk+hfW&_f0!W_d>#" },
    "L2": { "id": "a32fbe16f1b7266809gtzl", "ip": "192.168.0.26", "key": "F7V!uCsq_)}8Z&0Z" },
    "L3": { "id": "a370cf46b592f5595epwy3", "ip": "192.168.0.11", "key": "3]k?[]ngU$i92uY4" },
    "L4": { "id": "a30f584bfbf9d284a7fmqx", "ip": "192.168.0.18", "key": "dI)P1^}J|Y7gR++u" },
    "L5": { "id": "a3c247ab86da60363efgby", "ip": "192.168.0.16", "key": "*<b<^?80HS'Z5W-p" },
    "L6": { "id": "a3725ffe97304cebb5xvaq", "ip": "192.168.0.2",  "key": "kif!.]+o]/7Srzx0" }, 
    "L7": { "id": "a31b87b1fe8a5606ect45t", "ip": "192.168.0.4",  "key": "[:~/_xc!#]]vb1Q!" },
    "L8": { "id": "a37c5841ab5c0c1859542r", "ip": "192.168.0.6",  "key": "Q1zamU1ss`-T[4r7" }
}

# --- LIGHT SCENES ---
SCENE_DATA = {
    "L1": { 
        "FX1": "AckDHh4AAABFAAAAAAAA", 
        "FX2": "AcoFMDAIAABkAAAAAAAA", "FX3": "AcsMTk4AAABEAABkAABk",
        "FX5": "AcwEU1MAAABkAABkAOVk", "FX6": "Ac0KWVkAAAA6AAAAAAAA", "FX7": "Ac4MJCQAAABkAABkAABk",
        "FX9": "Ac8BMjIAAABkAABkAOpk"
    },
    "L2": { "FX1": "AckDHh4AAABFAAAAAAAA", "FX2": "AcoFMDAIAABkAAAAAAAA", "FX3": "AcsMTk4AAABEAABkAABk", "FX5": "AcwEU1MAAABkAABkAOdk", "FX7": "Ac0MIyMAAABkAOJkAOhk" },
    "L3": { "FX1": "AckDHh4AAABkAAAAAAAA", "FX2": "AcoFMDAIAABkAAAAAAAA", "FX3": "AcsMTk4AAABEAABkAABk", "FX5": "AcwEU1MAAABkAABkAN5k", "FX7": "Ac0MIyMAAABkAABkAABk" },
    "L4": { "FX1": "AckDHh4AAABMAAAAAAAA", "FX2": "AcoFMDAIAABkAAAAAAAA", "FX3": "AcsMTk4AAABEAABkAABk", "FX5": "AcwEU1MAAABkAABkANpk", "FX6": "Ac0KWVkAAAA6AAAAAAAA", "FX7": "Ac4MIyMAAABkAOBkAOBk" },
    "L5": { "FX1": "AckDHh4AAABkAAAAAAAA", "FX2": "AcoFMTEIAABkAAAAAAAA", "FX3": "AcsMTk4AAABEAABkAABk", "FX5": "AcwEU1MAAABkAABkAN1k", "FX6": "Ac0KWVkAAAA6AAAAAAAA", "FX7": "Ac4MIyMAAABkAABkAABk" },
    "L6": { "FX1": "AckDHh4AAABkAAAAAAAA", "FX2": "AcoFMDAIAABkAAAAAAAA", "FX3": "AcsMTk4AAABEAABkAABk", "FX5": "AcwEU1MAAABkAABkAN1k", "FX6": "Ac0KWVkAAAA6AAAAAAAA", "FX7": "Ac4MIyMAAABkANtkAOBk" },
    "L7": { "FX1": "AckDHh4AAABkAAAAAAAA", "FX2": "AcoFMDAIAABkAAAAAAAA", "FX3": "AcsMTk4AAABEAABkAABk", "FX5": "AcwEU1MAAABkAABkANxk", "FX6": "Ac0KWVkAAAA6AAAAAAAA", "FX7": "Ac4MJCQAAABkAABkAABk", "FX9": "Ac8BMjIAAABkAABkAO1k" },
    "L8": { "FX1": "AckDHh4AAABkAAAAAAAA", "FX2": "AcoFMTEIAABkAAAAAAAA", "FX3": "AcsMMjIAAABEAABkAABk", "FX5": "AcwEU1MAAABkAABkAOBk", "FX6": "Ac0KWVkAAAA6AAAAAAAA", "FX7": "Ac4MJCQAAABkANhkANlk", "FX9": "Ac8BMjIAAABkAABkAOdk" }
}

WHITE_SCENE_CODE = 'AdABMjIAAABkAAAAAAAA'

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
TEXT_H_TOP = ("SOMNITECH BIOLOGICS //\nFINAL LOG REPORT\n\nREPORT ID: T-RED-EXIT-[DATE/TIME]\n\nFINAL PROTOCOL INITIATED\n1: TERMINATE\n2: ASSIMILATE\n3: SUDDEN DEATH -\nCONSENSUS NOT ACHIEVED\n4: SUDDEN DEATH - TIMED OUT\n\nYou have come to the end of\nNeural Echos: Enter the Sleep\nLab. We hope you enjoyed\nyourselves.\n\nFOR POST-SHOW COMMENTARY, SCAN\nTHE CODE BELOW.\n")
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
#          PART 1: TUYA LIGHTS LOGIC
#        (PARALLEL WITH ANTI-FLOOD FIX)
# ==========================================

bulb_objects = {}
dim_timer = None 
CURRENT_STATE = None
SERVER_INSTANCE = None 

def broadcast(tags, func, *args):
    """
    Spawns a separate thread for each light so they all 
    receive the command at roughly the same time.
    """
    for tag in tags:
        t = threading.Thread(target=func, args=(tag, *args))
        t.start()
        time.sleep(0.1) 

def get_tuya_hex(h, s, v):
    h_hex = "{:04x}".format(h)
    s_hex = "{:04x}".format(s)
    v_hex = "{:04x}".format(v)
    return h_hex + s_hex + v_hex

def connect_all_lights():
    print(">>> [LIGHTS] Initializing 8 Lights...")
    for tag, conf in DEVICES_CONFIG.items():
        try:
            d = tinytuya.BulbDevice(conf['id'], conf['ip'], conf['key'])
            d.set_version(3.5)
            d.set_socketPersistent(True) 
            bulb_objects[tag] = d
            print(f"   ✅ {tag} Connected.")
        except Exception as e:
            print(f"   ❌ {tag} Failed: {e}")

def set_scene(tag, fx_name):
    device = bulb_objects.get(tag)
    if not device: return
    
    if tag in SCENE_DATA and fx_name in SCENE_DATA[tag]:
        code = SCENE_DATA[tag][fx_name]
        payload = {'21': 'scene', '51': code}
        
        for i in range(1, 4):  # Loop 1, 2, 3
            try:
                if i > 1: device.set_socketPersistent(True) # Refresh on retries
                device.send(device.generate_payload(tinytuya.CONTROL, payload))
                print(f"   -> {tag} >> SCENE {fx_name} (Signal {i})")
            except: 
                pass
            if i < 3: time.sleep(LIGHT_REPEAT_DELAY) # Don't sleep after the last one
    else:
        set_white(tag)

def set_white(tag):
    device = bulb_objects.get(tag)
    if not device: return
    
    payload = {'21': 'scene', '51': WHITE_SCENE_CODE}

    for i in range(1, 4):
        try:
            if i > 1: device.set_socketPersistent(True)
            device.send(device.generate_payload(tinytuya.CONTROL, payload))
            print(f"   -> {tag} >> WHITE (Signal {i})")
        except: 
            pass
        if i < 3: time.sleep(LIGHT_REPEAT_DELAY)

def set_color_hsv(tag, h, s, v):
    device = bulb_objects.get(tag)
    if not device: return
    
    hex_color = get_tuya_hex(h, s, v)
    payload = {'21': 'colour', '24': hex_color}

    for i in range(1, 4):
        try:
            if i > 1: device.set_socketPersistent(True)
            device.send(device.generate_payload(tinytuya.CONTROL, payload))
            print(f"   -> {tag} >> COLOR (Signal {i})")
        except: 
            pass
        if i < 3: time.sleep(LIGHT_REPEAT_DELAY)

def dim_lights_delayed():
    global CURRENT_STATE
    print(f"\n>>> [LIGHTS] 20s Elapsed. Dimming ({CURRENT_STATE}) to 50%...")
    
    def apply_dim(tag):
        if CURRENT_STATE == "red":
            set_color_hsv(tag, 0, 1000, 500) 
        elif CURRENT_STATE == "blue":
            set_color_hsv(tag, 240, 1000, 500)
        elif CURRENT_STATE == "white":
            device = bulb_objects.get(tag)
            try:
                device.send(device.generate_payload(tinytuya.CONTROL, {'22': 500}))
            except: pass

    broadcast(bulb_objects.keys(), apply_dim)

def start_dim_timer(state_name):
    global dim_timer, CURRENT_STATE
    CURRENT_STATE = state_name 
    if dim_timer:
        dim_timer.cancel()
    dim_timer = threading.Timer(20.0, dim_lights_delayed)
    dim_timer.start()

def handle_light_command(cmd):
    cmd = cmd.strip().strip('\x00')
    print(f"[LIGHTS] Processing Command: {cmd}")
    
    all_lights = ['L1', 'L2', 'L3', 'L4', 'L5', 'L6', 'L7', 'L8']
    
    if cmd.startswith("FX") and "10" not in cmd:
        if dim_timer: dim_timer.cancel()

    if cmd == "FX1":
        broadcast(all_lights, set_scene, "FX1")
        
    elif cmd == "FX2":
        broadcast(all_lights, set_scene, "FX2")
        
    elif cmd == "FX3":
        broadcast(['L1'], set_white)
        others = [l for l in all_lights if l != 'L1']
        broadcast(others, set_scene, "FX3")

    elif cmd == "FX4":
        broadcast(['L1', 'L2'], set_white)
        others = [l for l in all_lights if l not in ['L1', 'L2']]
        broadcast(others, set_scene, "FX2")
        
    elif cmd == "FX5":
        broadcast(all_lights, set_scene, "FX5")
        
    elif cmd == "FX6":
        broadcast(['L1', 'L2', 'L3'], set_white)
        others = [l for l in all_lights if l not in ['L1', 'L2', 'L3']]
        broadcast(others, set_scene, "FX6")
        
    elif cmd == "FX7":
        broadcast(all_lights, set_scene, "FX7")
        
    elif cmd == "FX8":
        whites = ['L1', 'L2', 'L3', 'L4', 'L5']
        broadcast(whites, set_white)
        others = ['L6', 'L7', 'L8']
        broadcast(others, set_scene, "FX6")
        
    elif cmd == "FX9":
        whites = ['L1', 'L2', 'L3', 'L4', 'L5', 'L6']
        broadcast(whites, set_white)
        others = ['L7', 'L8']
        broadcast(others, set_scene, "FX9")

    elif cmd == "FX10A": # Red
        broadcast(all_lights, set_color_hsv, 0, 1000, 1000)
        start_dim_timer("red")
        
    elif cmd == "FX10B": # Blue
        broadcast(all_lights, set_color_hsv, 240, 1000, 1000)
        start_dim_timer("blue")
        
    elif cmd == "FX10C": # White
        broadcast(all_lights, set_white)
        start_dim_timer("white")
        
    else:
        print(f"--> [LIGHTS] Unknown Command: {cmd}")

# ==========================================
#           PART 2: BLE PRINTER LOGIC
# ==========================================
def forward_to_sub_computer(command):
    """Broadcasts the trigger command to ANY computer listening on Port 53002."""
    print(f"[REMOTE PRINTER] Broadcasting '{command}' to Port {SUB_COMPUTER_PORT}...")
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        
        # REQUIRED: Allow this socket to send broadcast packets
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        
        sock.sendto(command.encode('utf-8'), (SUB_COMPUTER_IP, SUB_COMPUTER_PORT))
    except Exception as e:
        print(f"[REMOTE PRINTER] Error sending: {e}")
# ==========================================
#           PART 3: SAFE & RELAY LOGIC
# ==========================================

def relay_to_qlab(command):
    """Sends a string command to QLab via UDP"""
    print(f"[QLAB] Relaying: '{command}' to {QLAB_IP}:{QLAB_PORT}")
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.sendto(command.encode('utf-8'), (QLAB_IP, QLAB_PORT))
    except Exception as e:
        print(f"[QLAB] Error sending: {e}")

def send_safe_reset():
    """Sends 'RESETSAFE' UDP packet to the ENTIRE NETWORK"""
    try:
        print(f"[SAFE] Broadcasting Reset to Port {SAFE_PORT}...")
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)

        
        msg = b"RESETSAFE"
        sock.sendto(msg, (SAFE_IP, SAFE_PORT))
        print("[SAFE] Reset Command Broadcasted.")
    except Exception as e:
        print(f"[SAFE] Error sending reset: {e}")

class UnifiedUDPProtocol(asyncio.DatagramProtocol):
    def __init__(self, printer_address):
        self.printer_address = printer_address
        self.sing_step = 0
        self.sing_last_time = 0
        
        global SERVER_INSTANCE
        SERVER_INSTANCE = self

    def connection_made(self, transport):
        print("=" * 60)
        print(f"   UNIFIED SERVER LISTENING on {UDP_IP}:{UDP_PORT}")
        print("   (Receives from QLab, Safe, AND Singing Sensors)")
        print("   -> Relays Safe & Sing Triggers to QLab (Port 53535)")
        print("   -> Sends Reset to Safe (Port 4000)")
        print("=" * 60)

    def datagram_received(self, data, addr):
        raw_msg = data.decode('utf-8', errors='ignore')
        clean_msg = raw_msg.strip().strip('\x00')
        print(f"[UDP] Received: '{clean_msg}' from {addr}")
        
        # --- LOGIC BRANCHING ---

        # 1. CHECK FOR SINGING SEQUENCE (OR SING GO)
        # Check if the message is part of the sequence OR triggers the sequence final
        if clean_msg in SING_SEQUENCE or clean_msg == SING_QLAB_CMD:
            
            # >>>> ADDED DEBUG FOR NOTES <<<<
            print(f"🎹 [NOTE DETECTED] Processing: {clean_msg}")
            
            # >>> [UPDATE] IMMEDIATELY RELAY TO QLAB <<<
            # This makes sure the sound plays whenever the sensor triggers Python
            relay_to_qlab(clean_msg)
            
            # If it was just the "Sing" command, we are done
            if clean_msg == SING_QLAB_CMD:
                return

            # Otherwise, perform the Puzzle Logic
            now = time.time()
            
            # Check Timeout
            if self.sing_step > 0 and (now - self.sing_last_time > SING_MAX_GAP):
                print(f"❌ Singing too slow! Gap: {round(now - self.sing_last_time, 2)}s. Resetting.")
                relay_to_qlab(SING_FAIL_CMD) # Fail on Timeout
                self.sing_step = 0

            target_note = SING_SEQUENCE[self.sing_step]

            if clean_msg == target_note:
                # Correct Note!
                print(f"🎵 Step {self.sing_step + 1}/{len(SING_SEQUENCE)}: Received {clean_msg}")
                self.sing_step += 1
                self.sing_last_time = now

                # Completion Check
                if self.sing_step == len(SING_SEQUENCE):
                    print(f"🎉 SEQUENCE COMPLETE! Firing QLab: {SING_QLAB_CMD}")
                    relay_to_qlab(SING_QLAB_CMD)
                    self.sing_step = 0 # Reset
            
            elif clean_msg == SING_SEQUENCE[0]:
                 # User Restarted Sequence
                 print(f"🔄 Restarting sequence. Received {clean_msg}")
                 self.sing_step = 1
                 self.sing_last_time = now
            
            else:
                 # Wrong Note
                 if self.sing_step > 0:
                     print(f"❌ Wrong note. Expected {target_note}, got {clean_msg}. Resetting.")
                     # >>>> ADDED: FAIL ON WRONG NOTE <<<<
                     relay_to_qlab(SING_FAIL_CMD) 
                     self.sing_step = 0
            return

        # 2. TRIGGER FROM ARDUINO (SAFE) -> RELAY TO QLAB
        if clean_msg == "/cue/SAFE/go":
            print("✅ Safe Trigger Received!")
            relay_to_qlab(clean_msg)
            return

        # 3. RESET COMMAND FROM QLAB -> SEND TO ARDUINO
        if clean_msg == "/cue/SAFE/reset":
            print("✅ Safe Reset Command Received")
            send_safe_reset()
            return
        
# 4. PRINTER COMMAND
        is_printer_cmd = False
        
        # Use 'TRIGGERS' (which you defined at the top), not 'PRINTER_KEYS'
        for key in TRIGGERS:
            if key in clean_msg:
                is_printer_cmd = True
                break

        if is_printer_cmd:
            print(f"✅ Printer Trigger matched: {clean_msg}")
            # DIRECTLY forward to sub computer. No checks needed.
            forward_to_sub_computer(clean_msg)

        else:
            # 5. LIGHT COMMAND
            threading.Thread(target=handle_light_command, args=(clean_msg,)).start()

   
# ==========================================
#           PART 4: GUI & RESET LOGIC
# ==========================================

def trigger_manual_reset():
    print("\n" + "!"*40)
    print("!!! MANUAL RESET TRIGGERED !!!")
    print("!"*40)

    # --- PART A: Hardware/Internal Reset (Instant) ---
    # We do this FIRST so the lights/safe react immediately while the server reboots
    
    # 1. Reset Safe
    send_safe_reset()
    
    # 2. Reset Lights (Trigger FX1)
    threading.Thread(target=handle_light_command, args=("FX1",)).start()
    
    # 3. Reset Internal State (Singing sequence)
    global SERVER_INSTANCE
    if SERVER_INSTANCE:
        SERVER_INSTANCE.sing_step = 0
        print(">>> Internal Singing Step reset to 0.")
    else:
        print(">>> Warning: Server instance not ready yet.")

    # --- PART B: Software Reset (Threaded) ---
    # We define this function INSIDE trigger_manual_reset so it's a "local helper"
    def run_backend_reset_sequence():
        backend_dir = "/Users/christinechong/somnitech-fullstack/backend" 
        root_dir = "/Users/christinechong/somnitech-fullstack"

        try:
            # 1. STOP SERVER (Release DB locks first)
            print(">>> [THREAD] Stopping Server...")
            subprocess.run(["/bin/sh", "./stop.sh"], cwd=root_dir, check=True)
            print("✅ Server Stopped.")

            # 2. RESET DATA
            print(">>> [THREAD] Resetting Data...")
            subprocess.run(["/bin/sh", "./reset.sh"], cwd=backend_dir, check=True)
            print("✅ Data Reset.")

            # 3. START SERVER (Background)
            print(">>> [THREAD] Starting Server...")
            subprocess.Popen(["/bin/sh", "./start.sh"], cwd=root_dir) 
            print("✅ Server Start Initialized.")

        except subprocess.CalledProcessError as e:
            print(f"❌ [RESET ERROR] Script failed: {e}")
        except Exception as e:
            print(f"❌ [RESET ERROR] Execution failed: {e}")

    # NOW we can launch the thread using the function we just defined
    threading.Thread(target=run_backend_reset_sequence, daemon=True).start()

def setup_gui():
    root = tk.Tk()
    root.title("CONTROL")
    root.geometry("300x300")
    root.attributes('-topmost', True)
    
    label = tk.Label(root, text="ADMIN PANEL", font=("Arial", 12, "bold"))
    label.pack(pady=(10, 5))
    
    btn = tk.Button(root, 
                    text="RESET ALL\n(Safe / Lights / State / database) \n\n DO NOT RAGE AT CUSTOMERS", 
                    command=trigger_manual_reset, 
                    bg="#ff4444", 
                    fg="black", 
                    font=("Arial", 14, "bold"),
                    height=5,
                    width=25)
    btn.pack(pady=10)
    
    return root

# ==========================================
#                MAIN EXECUTION
# ==========================================

async def main():
    threading.Thread(target=connect_all_lights).start()
    
    # NOTE: We no longer connect to the printer here!
    
    root = setup_gui()
    print(">>> GUI Loaded.")
    
    loop = asyncio.get_running_loop()
    try:
        await loop.create_datagram_endpoint(
            lambda: UnifiedUDPProtocol(None),
            local_addr=(UDP_IP, UDP_PORT)
        )
        print("System Ready.")
        
        while True:
            try:
                root.update()
            except tk.TclError:
                break
            await asyncio.sleep(0.05) 
            
    except OSError as e:
        print(f"Network Error: {e}")
    except asyncio.CancelledError:
        print("Stopping...")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nScript terminated.")
