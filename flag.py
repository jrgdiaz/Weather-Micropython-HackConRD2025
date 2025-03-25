import machine, neopixel
from machine import Pin
import aioble
import asyncio
import time
from random import randint
import random

def clear_all_leds():

        NUM_LEDS = 31
        PIN = 2
        np = neopixel.NeoPixel(machine.Pin(PIN),NUM_LEDS)
        np.fill((0,0,0))
        np.write()

async def flag_colors():
    # Configuration
    NUM_LEDS = 31
    LEDS_PIN = 2
    COLORS = [(255, 0, 0), (255, 255, 255), (0, 0, 255)]  # Red, White, Blue
    BRIGHTNESS = 0.070  # Set brightness level (0.0 = off, 1.0 = full brightness)
    DELAY = 0.05
    FADE_STEPS = 20  # Steps for smooth transition

    # Initialize NeoPixel strip
    np = neopixel.NeoPixel(machine.Pin(LEDS_PIN), NUM_LEDS)

    while True:
        # Select a random LED to change
        i = random.randint(0, NUM_LEDS - 1)
        new_color = random.choice(COLORS)  # Pick a new color
        start_color = list(np[i])  # Get current color
        
        # Compute fade steps
        r_step = (new_color[0] - start_color[0]) / FADE_STEPS
        g_step = (new_color[1] - start_color[1]) / FADE_STEPS
        b_step = (new_color[2] - start_color[2]) / FADE_STEPS

        # Smoothly transition the color
        for step in range(FADE_STEPS):
            faded_color = (
                int((start_color[0] + r_step * step) * BRIGHTNESS),
                int((start_color[1] + g_step * step) * BRIGHTNESS),
                int((start_color[2] + b_step * step) * BRIGHTNESS),
            )
            np[i] = faded_color
            np.write()
            try:
                await asyncio.sleep(DELAY / FADE_STEPS)
            except asyncio.CancelledError:
                clear_all_leds()
                print("[+] Caught cancellation request, flag animation stopped")    
                break
        await asyncio.sleep(DELAY)  # Small delay before the next color shift


async def run_main():
    NUM_LEDS = 31
    LEDS_PIN = 2
    np = neopixel.NeoPixel(machine.Pin(LEDS_PIN), NUM_LEDS)
    clear_all_leds()
    flag_colors_animation = asyncio.create_task(flag_colors())
    await asyncio.gather(flag_colors_animation)
async def main():
    await run_main()
asyncio.run(main())
