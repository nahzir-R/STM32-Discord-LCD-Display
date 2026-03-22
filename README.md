# STM32 Discord LCD Display

A real-time embedded system that receives Discord messages over Ethernet and displays them on a 16x2 I2C LCD. Built on the STM32F767ZI (Cortex-M7) using FreeRTOS and the LwIP TCP/IP stack.

## Demo
*Demo video coming soon*

## System Architecture

Discord API >> Python Proxy (HTTP Server) >> Ethernet >> STM32F767ZI >> I2C >> 16x2 LCD


The STM32 polls the Python proxy over HTTP every 5 seconds. The proxy runs on a PC, listens for Discord messages via the Discord API, and serves the latest message as plain text over HTTP on port 8000.

## Hardware

- STM32F767ZI NUCLEO-144 development board
- 16x2 HD44780 LCD with PCF8574 I2C backpack
- Ethernet cable (direct to PC or connect to network)

## Software

- **FreeRTOS** (CMSIS-V1) — multi-task scheduling
- **LwIP 2.1.2** — TCP/IP stack with BSD socket API
- **STM32 HAL** — Ethernet (RMII), I2C peripheral drivers
- **Python** — discord.py, HTTP server for proxy

## Technical Details

- **Ethernet PHY:** LAN8742A in RMII mode (PG11 TX_EN, PG13 TXD0)
- **Clock:** HSE bypass at 8MHz from ST-LINK, PLL to 216MHz
- **MPU:** Configured with dedicated regions for Ethernet DMA descriptors at 0x2007C000
- **Linker:** Custom sections (.RxDescripSection, .TxDescripSection) in dedicated SRAM
- **LCD:** HD44780 via PCF8574 I2C expander (PB8 SCL, PB9 SDA) with DWT microsecond timing

## FreeRTOS Task Architecture

| Task | Priority | Function |
|------|----------|----------|
| EthIf | Realtime | Ethernet packet input (interrupt-driven) |
| ethernet_link | Normal | PHY link state monitoring |
| HttpPollTask | Normal | HTTP GET to proxy every 5 seconds |
| printMessage | Normal | LCD display updates via queue |

## Hardware Challenges

Getting Ethernet working on the NUCLEO-F767ZI required several non-obvious fixes:

1. Wrong TX pins — CubeMX defaults to PB11/PB12 but the NUCLEO-F767ZI routes ETH_TX_EN to PG11 and ETH_TXD0 to PG13
2. Clock misconfiguration — HSE input frequency must be set to 8MHz (ST-LINK clock) not 25MHz
3. Boot delay — required before HAL_Init() to allow clock stabilization on cold boot
4. MPU regions — Ethernet DMA descriptors must be placed in non-cacheable shareable SRAM with correct MPU attributes
5. Linker sections — DMA descriptor sections must be placed at specific SRAM addresses (0x2007C000)

## Getting Started

### STM32 Firmware
1. Open `STM32/` in STM32CubeIDE
2. Build and flash to NUCLEO-F767ZI
3. Set your PC Ethernet adapter to static IP `192.168.1.9`

### Python Proxy
1. Install dependencies:
```
pip install discord.py
```
2. Add your Discord bot token to `proxy/discord_lcd_bot.py`
3. Run:
```
python discord_lcd_bot.py
```

## Static IP Configuration

The STM32 is configured with static IP `192.168.1.100`. Your PC Ethernet adapter should be set to `192.168.1.9` on the same subnet.
