#!/usr/bin/env python3
"""SecTool V2 原理图 — 精确网格对齐版"""
import os, logging
logging.getLogger("kicad_sch_api").setLevel(logging.ERROR)
os.environ["KICAD_SYMBOL_DIR"] = "/mnt/c/Users/29037/AppData/Local/Programs/KiCad/10.0/share/kicad/symbols"

import kicad_sch_api as ksa

OUT = "/mnt/c/Users/29037/Desktop/SecToolV2.kicad_sch"
sch = ksa.create_schematic("SecTool V2")
sch._data["paper"] = "A2"  # 594x420mm

_flg = [0]
def add(lib, ref, val, x, y, **kw):
    return sch.components.add(lib, ref, val, position=(x, y), **kw)

def pwr(name, x, y, rot=0):
    _flg[0] += 1
    return sch.components.add(f"power:{name}", f"FLG{_flg[0]}", name, position=(x, y), rotation=rot)

def w(*pts):
    """画多段线 w(x1,y1, x2,y2, x3,y3, ...)"""
    coords = list(pts)
    for i in range(0, len(coords)-2, 2):
        sch.add_wire(start=(coords[i], coords[i+1]), end=(coords[i+2], coords[i+3]))

def lbl(text, x, y):
    sch.add_label(text=text, position=(x, y))

def jnc(x, y):
    sch.junctions.add(position=(x, y))

def nc(x, y):
    sch.no_connects.add(position=(x, y))

def P(ref, num):
    comp = sch.components.get(ref)
    pp = comp._data.get_pin_position(str(num))
    return (round(pp.x, 2), round(pp.y, 2))

def pin_pwr(ref, num, power_name, length=5.08):
    """引脚 → 垂直短线 → 电源符号"""
    px, py = P(ref, num)
    if power_name == "GND":
        ey = py + length
        w(px, py, px, ey)
        pwr("GND", px, ey, 180)
    else:
        ey = py - length
        w(px, py, px, ey)
        pwr(power_name, px, ey)

def pin_lbl(ref, num, text, dx=0, dy=0):
    """引脚 → 短线 → 标号"""
    px, py = P(ref, num)
    if dx != 0:
        w(px, py, px + dx, py)
        lbl(text, px + dx, py)
    elif dy != 0:
        w(px, py, px, py + dy)
        lbl(text, px, py + dy)
    else:
        lbl(text, px, py)

def pin_nc(ref, num):
    px, py = P(ref, num)
    nc(px, py)

# ================================================================
#  放置元件 (A2: 594×420mm)
# ================================================================
print("放置元件...")

# ── 封装定义 ──
FP_USB_C    = "Connector_USB:USB_C_Receptacle_HRO_TYPE-C-31-M-12"
FP_TP4056   = "Package_SO:TSSOP-8_4.4x3mm_P0.65mm"
FP_R0805    = "Resistor_SMD:R_0805_2012Metric"
FP_C0805    = "Capacitor_SMD:C_0805_2012Metric"
FP_LED0805  = "LED_SMD:LED_0805_2012Metric"
FP_JST2P    = "Connector_JST:JST_PH_B2B-PH-K_1x02_P2.00mm_Vertical"
FP_SW_SPDT  = "Button_Switch_SMD:SW_SPDT_CK_JS102011SAQN"
FP_SOT223   = "Package_TO_SOT_SMD:SOT-223-3_TabPin2"
FP_ESP32S3  = "RF_Module:ESP32-S3-WROOM-1"
FP_SW_PUSH  = "Button_Switch_THT:SW_PUSH_6mm"
FP_BUZZER   = "Buzzer_Beeper:Buzzer_12x9.5RM7.6"
FP_PIN1x02  = "Connector_PinHeader_2.54mm:PinHeader_1x02_P2.54mm_Vertical"
FP_PIN1x04  = "Connector_PinHeader_2.54mm:PinHeader_1x04_P2.54mm_Vertical"
FP_PIN1x06  = "Connector_PinHeader_2.54mm:PinHeader_1x06_P2.54mm_Vertical"
FP_PIN1x08  = "Connector_PinHeader_2.54mm:PinHeader_1x08_P2.54mm_Vertical"
FP_PIN2x04  = "Connector_PinHeader_2.54mm:PinHeader_2x04_P2.54mm_Vertical"

# ── 电源区 y=40~100 ──
add("Connector:USB_C_Receptacle",          "USB1", "USB-C",    70,  60, footprint=FP_USB_C)
add("Battery_Management:TP4056-42-ESOP8",  "U4",   "TP4056",  140, 60, footprint=FP_TP4056)
add("Device:R",                            "R5",   "1.2K",    155, 88, footprint=FP_R0805)
add("Connector_Generic:Conn_01x02",        "J1",   "BAT",     190, 60, footprint=FP_JST2P)
add("Switch:SW_Push",                      "SW6",  "PWR",     220, 60, footprint=FP_SW_SPDT)
add("Regulator_Linear:AMS1117-3.3",        "U2",   "AMS1117", 265, 60, footprint=FP_SOT223)
add("Device:C",                            "C1",   "10uF",    245, 88, footprint=FP_C0805)
add("Device:C",                            "C2",   "10uF",    265, 88, footprint=FP_C0805)
add("Device:C",                            "C3",   "100nF",   285, 88, footprint=FP_C0805)

# ── 主控区 y=130~210 ──
add("RF_Module:ESP32-S3-WROOM-1",          "U1",   "ESP32-S3", 200, 170, footprint=FP_ESP32S3)
add("Connector_Generic:Conn_01x04",        "H2",   "UART_DBG", 290, 165, footprint=FP_PIN1x04)

# ── 人机交互 y=240~340 ──
add("Connector_Generic:Conn_01x04",        "U3",   "OLED",     60, 270, footprint=FP_PIN1x04)
add("Device:R",                            "R1",   "4.7K",     85, 255, footprint=FP_R0805)
add("Device:R",                            "R2",   "4.7K",     95, 255, footprint=FP_R0805)
add("Device:R",                            "R3",   "330R",     60, 305, footprint=FP_R0805)
add("Device:LED",                          "LED1", "PWR",      60, 320, footprint=FP_LED0805)
add("Device:R",                            "R4",   "330R",     80, 305, footprint=FP_R0805)
add("Device:LED",                          "LED2", "STS",      80, 320, footprint=FP_LED0805)
add("Device:Buzzer",                       "BZ1",  "BUZ",     100, 315, footprint=FP_BUZZER)
add("Switch:SW_Push",                      "SW1",  "UP",      125, 285, footprint=FP_SW_PUSH)
add("Switch:SW_Push",                      "SW2",  "DN",      145, 285, footprint=FP_SW_PUSH)
add("Switch:SW_Push",                      "SW3",  "LT",      165, 285, footprint=FP_SW_PUSH)
add("Switch:SW_Push",                      "SW4",  "RT",      185, 285, footprint=FP_SW_PUSH)
add("Switch:SW_Push",                      "SW5",  "OK",      205, 285, footprint=FP_SW_PUSH)

# ── 扩展模块 y=240~340 ──
add("Connector_Generic:Conn_01x08",        "H4",   "RC522",    260, 285, footprint=FP_PIN1x08)
add("Connector_Generic:Conn_01x08",        "H5",   "CC1101",   295, 285, footprint=FP_PIN1x08)
add("Connector_Generic:Conn_02x04_Odd_Even","P1",  "SOP8",     330, 285, footprint=FP_PIN2x04)
add("Connector_Generic:Conn_01x08",        "CARD1","SD",        365, 285, footprint=FP_PIN1x08)
add("Connector_Generic:Conn_01x04",        "U5",   "I2C_EXT",  405, 285, footprint=FP_PIN1x04)
add("Connector_Generic:Conn_01x04",        "U6",   "UART_EXT", 435, 285, footprint=FP_PIN1x04)
add("Connector_Generic:Conn_01x06",        "H3",   "GPIO",     465, 285, footprint=FP_PIN1x06)

print(f"  {len(list(sch.components))} 元件")

# ================================================================
#  打印引脚映射（调试用）
# ================================================================
u4_comp = sch.components.get("U4")
print("\nTP4056 pins:")
for p in u4_comp.list_pins():
    pp = P("U4", p["number"])
    print(f"  {p['number']:>2} {p['name']:>10}: ({pp[0]}, {pp[1]})")

# ================================================================
#  布线
# ================================================================
print("\n布线...")

# ──── A: 电源系统 ────

# USB1: VBUS(A4) → +5V, GND(A1) → GND
# 注：A4/A9/B4/B9 坐标相同，A1/A12/B1/B12 坐标相同，只需各连一次
pin_pwr("USB1", "A4", "+5V")
pin_pwr("USB1", "A1", "GND")
# USB D+/D-（A6/B6 坐标不同，都要连）
pin_lbl("USB1", "A6", "USB_DP", dx=10.16)
pin_lbl("USB1", "A7", "USB_DN", dx=10.16)
pin_lbl("USB1", "B6", "USB_DP", dx=10.16)
pin_lbl("USB1", "B7", "USB_DN", dx=10.16)
# CC1/CC2 → NC（不用 USB PD）
pin_nc("USB1", "A5")
pin_nc("USB1", "B5")
# SBU1/SBU2 → NC
pin_nc("USB1", "A8")
pin_nc("USB1", "B8")
# 高速差分对 → NC（只用 USB 2.0）
for pn in ["A2","A3","A10","A11","B2","B3","B10","B11"]:
    pin_nc("USB1", pn)
# SHIELD → GND
pin_pwr("USB1", "SH", "GND")

# TP4056 (ESOP-8 实际引脚):
# 1=TEMP, 2=PROG, 3=GND, 4=VCC, 5=BAT, 6=~STDBY, 7=~CHRG, 8=CE, 9=EPAD
pin_pwr("U4", "4", "+5V")        # VCC → +5V
pin_pwr("U4", "3", "GND")        # GND
pin_pwr("U4", "9", "GND")        # EPAD → GND
pin_pwr("U4", "1", "GND")        # TEMP → GND
pin_lbl("U4", "5", "BAT", dx=10) # BAT

# PROG(U4.2) → R5.pin1(上) → R5.pin2(下) → GND
p_prog = P("U4", "2")
p_r5_1 = P("R5", "1")  # R5 上端
w(p_prog[0], p_prog[1], p_r5_1[0], p_prog[1], p_r5_1[0], p_r5_1[1])
pin_pwr("R5", "2", "GND")

# CE(pin8) → VCC (enable, 拉高)
pin_pwr("U4", "8", "+5V", length=7.62)

# ~STDBY(pin6), ~CHRG(pin7) → NC (开漏输出，不接)
pin_nc("U4", "6")
pin_nc("U4", "7")

# J1 电池座: pin1→BAT, pin2→GND
pin_lbl("J1", "1", "BAT", dx=-10)
pin_pwr("J1", "2", "GND")

# SW6 开关: pin1→BAT, pin2→VIN
pin_lbl("SW6", "1", "BAT", dx=-10)
pin_lbl("SW6", "2", "VIN", dx=10)

# U2 AMS1117: pin3=VI→VIN, pin2=VO→VCC, pin1=GND
pin_lbl("U2", "3", "VIN", dx=-10.16)
pin_lbl("U2", "2", "VCC", dx=10.16)
pin_pwr("U2", "1", "GND")

# C1: pin1(上)→VIN, pin2(下)→GND
pin_lbl("C1", "1", "VIN", dy=-7.62)
pin_pwr("C1", "2", "GND")

# C2: pin1(上)→VCC, pin2(下)→GND
pin_pwr("C2", "1", "VCC")
pin_pwr("C2", "2", "GND")

# C3: pin1(上)→VCC, pin2(下)→GND
pin_pwr("C3", "1", "VCC")
pin_pwr("C3", "2", "GND")

# PWR_FLAG 驱动 +5V net 和 GND net
# +5V PWR_FLAG：放 PWR_FLAG，连到 +5V 符号
pf_5v = pwr("PWR_FLAG", 280, 40)
pf_5v_p = P(f"FLG{_flg[0]}", "1")
p5v = pwr("+5V", pf_5v_p[0], pf_5v_p[1] + 5.08)
p5v_p = P(p5v.reference, "1")
w(pf_5v_p[0], pf_5v_p[1], p5v_p[0], p5v_p[1])

# GND PWR_FLAG
pf_gnd = pwr("PWR_FLAG", 290, 105, 180)
pf_gnd_p = P(f"FLG{_flg[0]}", "1")
pgnd = pwr("GND", pf_gnd_p[0], pf_gnd_p[1] - 5.08, 180)
pgnd_p = P(pgnd.reference, "1")
w(pf_gnd_p[0], pf_gnd_p[1], pgnd_p[0], pgnd_p[1])

# VIN PWR_FLAG（SW6 输出 → AMS1117 输入的中间 net）
pf_vin = pwr("PWR_FLAG", 300, 40)
pf_vin_p = P(f"FLG{_flg[0]}", "1")
w(pf_vin_p[0], pf_vin_p[1], pf_vin_p[0], pf_vin_p[1] + 5.08)
lbl("VIN", pf_vin_p[0], pf_vin_p[1] + 5.08)

# ──── B: ESP32-S3 ────
print("  ESP32...")

pin_pwr("U1", "2", "VCC")    # 3V3 �� VCC
pin_pwr("U1", "1", "GND")    # GND
pin_pwr("U1", "40", "GND")
pin_pwr("U1", "41", "GND")

# EN → VCC（先放电源符号，用其引脚坐标画线）
p_en = P("U1", "3")
vcc_en = pwr("VCC", p_en[0]+10.16, p_en[1]-7.62)
vcc_en_p = P(vcc_en.reference, "1")
w(p_en[0], p_en[1], vcc_en_p[0], p_en[1], vcc_en_p[0], vcc_en_p[1])

# 信号引脚标号
u1_comp = sch.components.get("U1")
u1_name2num = {p["name"]: p["number"] for p in u1_comp.list_pins()}

signal_map = {
    "IO4": "SDA", "IO5": "SCL",
    "IO6": "KEY_UP", "IO7": "KEY_DN",
    "IO8": "LED_STS",
    "IO9": "RC522_CS", "IO10": "SPI_CLK", "IO11": "SPI_MOSI", "IO12": "SPI_MISO",
    "IO3": "RC522_RST",
    "IO13": "SD_MOSI", "IO14": "SD_CLK",
    "IO15": "KEY_LT", "IO16": "KEY_RT", "IO17": "KEY_OK",
    "IO21": "SD_MISO", "IO47": "SD_CS",
    "IO35": "FLASH_CS", "IO36": "FLASH_DO", "IO37": "FLASH_CLK", "IO38": "FLASH_DI",
    "IO39": "UART_TX", "IO40": "UART_RX",
    "IO41": "GPIO1", "IO42": "GPIO2", "IO1": "GPIO3", "IO2": "GPIO4",
    "IO45": "CC1101_GDO0", "IO46": "CC1101_CS",
    "IO48": "BUZZER",
    "TXD0": "TXD0", "RXD0": "RXD0",
    "USB_D-": "USB_DN", "USB_D+": "USB_DP",
}

connected_esp = set()
for pin_name, net_name in signal_map.items():
    num = u1_name2num.get(pin_name)
    if not num: continue
    px, py = P("U1", num)
    center_x = 200  # U1 center
    if px < center_x:
        pin_lbl("U1", num, net_name, dx=-10)
    else:
        pin_lbl("U1", num, net_name, dx=10)
    connected_esp.add(num)

# IO0, IO18 未用 → NC
for pin_name in ["IO0", "IO18"]:
    num = u1_name2num.get(pin_name)
    if num and num not in connected_esp:
        pin_nc("U1", num)
        connected_esp.add(num)

# ──── C: 人机交互 ────
print("  人机交互...")

# OLED: pin1→VCC, pin2→GND, pin3→SCL, pin4→SDA
pin_pwr("U3", "1", "VCC")
pin_pwr("U3", "2", "GND")
pin_lbl("U3", "3", "SCL", dx=-10)
pin_lbl("U3", "4", "SDA", dx=-10)

# R1 SCL上拉: pin1(上)→VCC, pin2(下)→SCL
pin_pwr("R1", "1", "VCC")
pin_lbl("R1", "2", "SCL", dy=7.62)

# R2 SDA上拉: pin1(上)→VCC, pin2(下)→SDA
pin_pwr("R2", "1", "VCC")
pin_lbl("R2", "2", "SDA", dy=7.62)

# R3→LED1 电源灯: pin1(上)→VCC, pin2(下)→LED1.A(右)
pin_pwr("R3", "1", "VCC")
r3b = P("R3", "2")
led1a = P("LED1", "2")
w(r3b[0], r3b[1], led1a[0], led1a[1])
pin_pwr("LED1", "1", "GND", length=7.62)

# R4→LED2 状态灯: pin1(上)→LED_STS, pin2(下)→LED2.A(右)
pin_lbl("R4", "1", "LED_STS", dy=-7.62)
r4b = P("R4", "2")
led2a = P("LED2", "2")
w(r4b[0], r4b[1], led2a[0], led2a[1])
pin_pwr("LED2", "1", "GND", length=7.62)

# BZ1: pin1(+,上)→BUZZER, pin2(-,下)→GND
pin_lbl("BZ1", "1", "BUZZER", dy=-7.62)
pin_pwr("BZ1", "2", "GND")

# 按键: pin1→信号, pin2→GND
for ref, net in [("SW1","KEY_UP"),("SW2","KEY_DN"),("SW3","KEY_LT"),("SW4","KEY_RT"),("SW5","KEY_OK")]:
    pin_lbl(ref, "1", net, dx=-10)
    pin_pwr(ref, "2", "GND")

# ──── D: 扩展模块 ────
print("  扩展模块...")

# H2 UART调试
pin_pwr("H2", "1", "VCC")
pin_pwr("H2", "2", "GND")
pin_lbl("H2", "3", "TXD0", dx=-10)
pin_lbl("H2", "4", "RXD0", dx=-10)

# H4 RC522
pin_pwr("H4", "1", "VCC")
pin_pwr("H4", "2", "GND")
pin_lbl("H4", "3", "SPI_CLK", dx=-10)
pin_lbl("H4", "4", "SPI_MOSI", dx=-10)
pin_lbl("H4", "5", "SPI_MISO", dx=-10)
pin_lbl("H4", "6", "RC522_CS", dx=-10)
pin_lbl("H4", "7", "RC522_RST", dx=-10)
pin_nc("H4", "8")

# H5 CC1101
pin_pwr("H5", "1", "VCC")
pin_pwr("H5", "2", "GND")
pin_lbl("H5", "3", "SPI_CLK", dx=-10)
pin_lbl("H5", "4", "SPI_MOSI", dx=-10)
pin_lbl("H5", "5", "SPI_MISO", dx=-10)
pin_lbl("H5", "6", "CC1101_CS", dx=-10)
pin_lbl("H5", "7", "CC1101_GDO0", dx=-10)
pin_nc("H5", "8")

# P1 SOP8 (2x4)
pin_lbl("P1", "1", "FLASH_CS", dx=-10)
pin_lbl("P1", "2", "FLASH_DO", dx=10)
pin_pwr("P1", "3", "VCC")
pin_lbl("P1", "4", "FLASH_DI", dx=10)
pin_lbl("P1", "5", "FLASH_CLK", dx=-10)
pin_nc("P1", "6")
pin_nc("P1", "7")
pin_pwr("P1", "8", "GND")

# CARD1 SD
pin_lbl("CARD1", "1", "SD_CS", dx=-10)
pin_lbl("CARD1", "2", "SD_MOSI", dx=-10)
pin_pwr("CARD1", "3", "GND")
pin_pwr("CARD1", "4", "VCC")
pin_lbl("CARD1", "5", "SD_CLK", dx=-10)
pin_pwr("CARD1", "6", "GND")
pin_lbl("CARD1", "7", "SD_MISO", dx=-10)
pin_nc("CARD1", "8")

# U5 I2C扩展
pin_pwr("U5", "1", "VCC")
pin_pwr("U5", "2", "GND")
pin_lbl("U5", "3", "SCL", dx=-10)
pin_lbl("U5", "4", "SDA", dx=-10)

# U6 UART扩展
pin_pwr("U6", "1", "VCC")
pin_pwr("U6", "2", "GND")
pin_lbl("U6", "3", "UART_TX", dx=-10)
pin_lbl("U6", "4", "UART_RX", dx=-10)

# H3 GPIO扩展
pin_pwr("H3", "1", "VCC")
pin_pwr("H3", "2", "GND")
pin_lbl("H3", "3", "GPIO1", dx=-10)
pin_lbl("H3", "4", "GPIO2", dx=-10)
pin_lbl("H3", "5", "GPIO3", dx=-10)
pin_lbl("H3", "6", "GPIO4", dx=-10)

# ================================================================
sch.save(OUT)
total = len(list(sch.components))
wires = len(list(sch.wires))
labels = len(list(sch.labels))
print(f"\n=== 完成 ===")
print(f"  元件: {total}, 导线: {wires}, 标号: {labels}")
print(f"  → {OUT}")
