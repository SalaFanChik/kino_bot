from aiogram import executor
from handlers import dp
import asyncio
from db import main

if __name__ == '__main__':
    loop  = asyncio.get_event_loop()
    loop.run_until_complete(asyncio.gather(main()))

    executor.start_polling(dp, skip_updates=True)
