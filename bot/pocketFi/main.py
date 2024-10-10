import asyncio
import aiohttp
import brotli
from loguru import logger
import time

logger.add('runtime.log', rotation='10 MB', colorize=True)

class PocketFiBot:
    def __init__(self, data):
        # 初始化时传入的用户数据
        self.data = data

    # 领取未燃烧的switch
    async def claimSwitch(self):
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
                # 解析 JSON 响应
                json_response = await response.json()
                # logger.info(f'response is: {json_response}')
                # 毫秒时间戳
                endTimestamp = json_response.get('1728584580035')

                # 将毫秒时间戳转换为秒时间戳
                timestamp_s = timestamp_ms / 1000

                # 将时间戳转换为本地时间的时间结构
                time_struct = time.localtime(timestamp_s)

                # 格式化输出时间
                formatted_time = time.strftime('%Y-%m-%d %H:%M:%S', time_struct)
                print(formatted_time)  

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
                        await self.doSignIn(data)
                    else:
                        logger.info(f'今日天已完成签到!')
                else:
                    logger.error(f'error code is: {status_code}')

    # 进行签到
    async def doSignIn(self):    
        url = 'https://rubot.pocketfi.org/boost/activateDailyBoost'
        headers = {
                'Accept': '*/*',
                'Accept-Encoding': 'gzip, deflate, br',
                'Accept-Language': 'zh-CN,zh-Hans;q=0.9',
                'Connection': 'keep-alive',
                'Content-Length': '0',
                'Host': 'rubot.pocketfi.org',
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
                    logger.info(f'今日天已完成签到!')
                else:
                    logger.error(f'签到失败:error code is: {status_code}')


data = 'query_id=AAEphxN_AAAAACmHE39Fk4-H&user=%7B%22id%22%3A2131986217%2C%22first_name%22%3A%22nuan%22%2C%22last_name%22%3A%22Yu%22%2C%22username%22%3A%22Mandorala%22%2C%22language_code%22%3A%22zh-hans%22%2C%22allows_write_to_pm%22%3Atrue%7D&auth_date=1728552265&hash=3fa5840b2634f1e003582d88fe23f1f3aace5659bdaaf30b87a6b295e725a9c4'

bot = PocketFiBot(data)
asyncio.run(bot.claimSwitch())




# {
# 	'userMining': {
# 		'userId': 2131986217,
# 		'speed': 0.29531250000000003,
# 		'dttmLastClaim': 1728562980035,
# 		'miningAmount': 0,
# 		'status': 0,
# 		'gotAmount': 87.18632812499997,
# 		'sentNotificationAmount': 0,
# 		'guild': 1,
# 		'alliance': 'mlwex',
# 		'dttmClaimDeadline': 1728584580035,
# 		'dttmLastPayment': 1728562500000,
# 		'withheld': False
# 	}
# }