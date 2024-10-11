import asyncio
import aiohttp
import brotli
from loguru import logger
from datetime import datetime, timedelta

logger.add('runtime.log', rotation='10 MB', colorize=True)

class PocketFiBot:
    def __init__(self, data):
        # 初始化时传入的用户数据
        self.data = data

    # 领取未燃烧的switch
    async def getClaimTime(self):
        url = 'https://gm.pocketfi.org/mining/claimMining'
        headers = {
                'Accept': '*/*',
                'Accept-Encoding': 'gzip, deflate, br',
                'Accept-Language': 'zh-CN,zh-Hans;q=0.9',
                'Connection': 'keep-alive',
                'Content-Length': '0',
                'Host': 'gm.pocketfi.org',
                'Origin': 'https://botui.pocketfi.org',
                'Referer': 'https://botui.pocketfi.org/',
                'Sec-Fetch-Dest': 'empty',
                'Sec-Fetch-Mode': 'cors',
                'Sec-Fetch-Site': 'same-site',
                'telegramRawData': self.data,
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko)',
                'x-paf-t': 'Abvx2NzMTM=='
            }

        async with aiohttp.ClientSession() as session:
            async with session.post(url, headers=headers) as response:
                if response.status == 200:
                    json_response = await response.json()
                    gotAmount = json_response.get('userMining', {}).get('gotAmount', None)
                    logger.info(f'领取成功,当前switch数量：{gotAmount}!')
                    endTimestamp = json_response.get('userMining', {}).get('dttmClaimDeadline', None)
                    if endTimestamp:
                        return endTimestamp / 1000
                    else:
                        logger.error("Response missing 'dttmClaimDeadline'.")
                        return None
                else:
                    logger.error(f'claimMining occur error: {response.status}')
                    return None

    # 查询当天是否已完成签到
    async def checkSignStatus(self):    
        url = 'https://bot.pocketfi.org/mining/taskExecuting'
        headers = {
                'Accept': '*/*',
                'Accept-Encoding': 'gzip, deflate, br',
                'Accept-Language': 'zh-CN,zh-Hans;q=0.9',
                'Connection': 'keep-alive',
                'Content-Length': '0',
                'Host': 'bot.pocketfi.org',
                'Origin': 'https://pocketfi.app',
                'Referer': 'https://pocketfi.app/',
                'Sec-Fetch-Dest': 'empty',
                'Sec-Fetch-Mode': 'cors',
                'Sec-Fetch-Site': 'cross-site',
                'telegramRawData': self.data,
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko)',
                'x-paf-t': 'Abvx2NzMTM=='
            }
        
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=headers) as response:
                # 解析 JSON 响应
                status_code = response.status
                if status_code == 200:
                    json_response = await response.json()
                    dailyTask = json_response.get('tasks', {}).get('daily')[0]
                    currentDay = dailyTask.get('currentDay')
                    if dailyTask.get('doneAmount') == 0:
                        logger.info(f'第{currentDay + 1}天还未签到!')
                        await self.doSignIn()
                    else:
                        logger.info(f'今日天已完成签到!')
                else:
                    logger.error(f'error code is: {status_code}')

    # 进行签到
    async def doSignIn(self):    
        url = 'https://bot.pocketfi.org/boost/activateDailyBoost'
        headers = {
                'Accept': '*/*',
                'Accept-Encoding': 'gzip, deflate, br',
                'Accept-Language': 'zh-CN,zh-Hans;q=0.9',
                'Connection': 'keep-alive',
                'Content-Length': '0',
                'Host': 'bot.pocketfi.org',
                'Origin': 'https://pocketfi.app',
                'Referer': 'https://pocketfi.app/',
                'Sec-Fetch-Dest': 'empty',
                'Sec-Fetch-Mode': 'cors',
                'Sec-Fetch-Site': 'cross-site',
                'telegramRawData': self.data,
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko)',
                'x-paf-t': 'Abvx2NzMTM=='
            }
        
        async with aiohttp.ClientSession() as session:
            async with session.post(url, headers=headers) as response:
                # 解析 JSON 响应
                status_code = response.status
                if status_code == 200:
                    json_response = await response.json()
                    logger.info(f'今日天已完成签到!')
                else:
                    logger.error(f'签到失败:error code is: {status_code}')
                
            
    async def startScheduler(self):
        await self.checkSignStatus()
        next_time = await self.getClaimTime()

        if next_time:
            # 将 Unix 时间戳转换为 datetime 对象
            next_time_datetime = datetime.fromtimestamp(next_time)
            logger.info(f"下次领取时间: {next_time_datetime}")

            # 计算提前 20 到 30 分钟的随机时间
            delay_time = timedelta(minutes=20)
            time_until_next_call = next_time_datetime - datetime.now() - delay_time

            # 如果下一次调用时间已经过去，立即调用
            if time_until_next_call.total_seconds() <= 0:
                logger.info("Time passed, invoking the API immediately.")
            else:
                logger.info(f"休眠:{time_until_next_call.total_seconds()}秒后再次调用。")

                # 等待到目标时间前的 20 分钟
                await asyncio.sleep(time_until_next_call.total_seconds())

            # 再次递归调用
            await self.startScheduler()
        else:
            logger.error("领取失败,60S后重试。")
            await asyncio.sleep(60)
            await self.startScheduler()


data = 'query_id=AAEphxN_AAAAACmHE3_PbcpL&user=%7B%22id%22%3A2131986217%2C%22first_name%22%3A%22nuan%22%2C%22last_name%22%3A%22Yu%22%2C%22username%22%3A%22Mandorala%22%2C%22language_code%22%3A%22zh-hans%22%2C%22allows_write_to_pm%22%3Atrue%7D&auth_date=1728562588&hash=2c5d31c19dd06f65039678c01b4b9f16a6c85f452d2cc0bc6d75ad627243e099'
bot = PocketFiBot(data)
asyncio.run(bot.startScheduler())