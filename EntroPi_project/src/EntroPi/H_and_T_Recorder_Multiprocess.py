"""Use concurrent to run LCD update script and w1Therm script in parallel"""

import concurrent.futures
from humidity_and_temps_recorder import start_LCD_daemon, main_data_gathering_loop


with concurrent.futures.ProcessPoolExecutor() as executor:
    futures = [
        executor.submit(start_LCD_daemon), 
        executor.submit(main_data_gathering_loop)
        ]


results = [f.result() for f in futures]
