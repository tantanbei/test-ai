import requests
import json
import time
import random
from urllib.parse import quote
import argparse
import yaml
import re
from tqdm import tqdm

class ZhihuDirectAnswer:
    def __init__(self):
        self.headers = {
            'accept': '*/*',
            'accept-language': 'en-US,en;q=0.9,zh-CN;q=0.8,zh;q=0.7',
            'content-type': 'text/plain;charset=UTF-8',
            'origin': 'https://zhida.zhihu.com',
            'referer': 'https://zhida.zhihu.com/pro/search',
            'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36',
            'x-requested-with': 'fetch',
            'x-xsrftoken': 'n0TkHh7XTVvzljXpEAkkN1r3lZTgqsyF',
            'x-zse-93': '101_3_3.0',
            'x-zse-96': '2.0_0LwlD2AAL4pMd23lfVpis5mKnXa/gbusCVtpXBes7BR72GNQFT/cLbbtTK8LWbiZ'
        }
        self.cookies = {
            'd_c0': 'ARAaNv8odhiPTvdrJaZ6G_RDgA1eJOmWbc4=|1713026453',
            '_xsrf': 'n0TkHh7XTVvzljXpEAkkN1r3lZTgqsyF',
            '_zap': '64e926ed-5fa5-4c74-a694-6de047a04d2d',
            'Hm_lvt_98beee57fd2ef70ccdd5ca52b9740c49': '1741349604,1742182609',
            'HMACCOUNT': '00F898FC73B2B23A',
            'captcha_session_v2': '2|1:0|10:1742380648|18:captcha_session_v2|88:NDhBYlBCRkh3cFJKbHRQL09XNUl2WjdHRTBJRmxSRFNXK1lsTjFTdGZGL0JGNDN3VUUzSUt3L01IaFVlZ09HKw==|10882cc14c7e9a6ca91af120b8265fb69ca6869bfb4ae15a1de1c0ca82e448c5',
            '__snaker__id': 'OOFGqRLtt6CCb4kJ',
            'gdxidpyhxdE': 'dnGqWZCqzEhmKr519I%2BsrUMIhIe7twXk0lVoTKHm2I5fXPVRfEN4gPtk6CsdBks92s85T5VaVOknV8AmYEbR8IT1KcV2b7NGrVJ%2B%2F9lGMJI1%5CRZxV77ObHe%2B%2Bp4IurmN3Aum64GzbqSixvkbWLC%2FqzD51U2KsphyAO3%2FpG9PhNPpfekd%3A1742381550345',
            'z_c0': '2|1:0|10:1742539236|4:z_c0|92:Mi4xYjVvOEFnQUFBQUFCRUJvMl95aDJHQ1lBQUFCZ0FsVk5vdXpIYUFCWFlOTEtmQnRjQTViOG02WUdLcGxoWmMweFJB|047e7b2f5041ec1b8092926ff16498190124f0b6e7a8e572684ac6284387187f',
            '__zse_ck': '004_4KEqSlK6RNM7y/2gfpOoecgGce3uzbkMT9roaxptqxyaY0LQFsPhCnRnU78Gf8e=emm9EQ9Npe5JoWzBzl2tMP4EKq6yNsdB/AshoXYIgSnCAymQJUHx8S/E3jvH4Xly-ntM/Ygk2BR2f7Bs6vum9UZgUCFdesPfP/4dK5G8gddbm0MIGuZn9iXyBMAPNizKOrXyKF+Gw6SkC1ekJR5POwToRhl+0wtRQp+c6R/xJBhiJLyXmbm+WAfCT2O9ZSH0Y',
            'SESSIONID': 'ESljzcxVG1WaL2S1VKPYQiNOLG5vSEA7Pn4BnXwd2tT',
            'JOID': 'UloXA0lk20pFj4ulLWS7E6q9PPA-Cb0YdOTx8WtToAsqy_vASWXTlyKPiactejfTXLdAMVrLDYUoBGTJGdaU8xs=',
            'osd': 'Wl4SC01s309Ni4OhKGy_G664NPQ2DbgQcOz19GNXqA8vw__ITWDbkyqLjK8pcjPWVLNINV_DCY0sAWzNEdKR-x8=',
            'EDU_MEMBER_HASH_ID': '9f839f1a1f525d177a377e771e9092d0',
            'EDU_TRACE_ID': '67f5e6c4-06d4-4849-9124-0696e5f23349',
            'tst': 'r',
            'Hm_lpvt_98beee57fd2ef70ccdd5ca52b9740c49': '1742544039',
            'BEC': '5ee33e0856ed13c879689106c041a08d'
        }
        
    def create_task(self, prompt):
        url = 'https://zhida.zhihu.com/ai_ingress/ai_chat/send_message'
        
        data = {
            "tab_type": "zhida_pro",
            "message_content": prompt,
            "message_source_type": "text",
            "quiz_type": 0,
            "is_preview": False,
            "deep_thinking_enabled": True,
            "knowledge_ids": ["1","2","3"],
            "session_id": ""
        }
        
        response = requests.post(url, 
                               headers=self.headers, 
                               cookies=self.cookies, 
                               json=data)
        
        if response.status_code == 200:
            result = response.json()
            message_id = result.get('recv_message', {}).get('message_id')
            print(f"创建任务成功，message_id: {message_id}")
            return message_id
        else:
            print(f"创建任务失败，状态码: {response.status_code}")
        return None

    def get_result(self, message_id):
        url = f'https://zhida.zhihu.com/ai_ingress/ai_chat/polling_message?message_id={message_id}'
        
        retry_count = 0
        while True:
            response = requests.get(url, 
                                  headers=self.headers, 
                                  cookies=self.cookies)
            
            if response.status_code == 200:
                result = response.json()
                status = result.get('status', 0)
                print(f"轮询次数: {retry_count}, 状态: {status}")
                
                if status == 1:  # 数据更新完毕
                    print(f"获取结果成功，message_id: {message_id}")
                    return result.get('summary', '')
            else:
                print(f"轮询失败，状态码: {response.status_code}")
                
            retry_count += 1
            time.sleep(10)  # 等待1秒后再次查询
            
    def generate_conversation(self, job_description, core_technology):
        print(f"\n开始生成对话 - 角色: {job_description}, 技术: {core_technology}")
        
        prompt = f'''你现在是一个资深程序化广告专家，现任职于一家广告平台公司，核心目标是保证广告平台利益最大。
程序化广告公司简介：预算来源分为两部分，一部分来自开户平台，客户由销售洽谈接入进来，目前主要客户有百度系、阿里系、头条系等，客户投放方式主要依赖ocpm，主要预算考核目标有首次拉活、激活、次留等，有少量cpm和cpc出价预算，定向方式有性别、年龄、人群包、时段、rta等，主要涉及的开发有广告算法、广告检索技术和广告平台技术。另一部分预算来自于dsp，dsp由商务引入，广告检索技术负责对接开发，dsp都是rtb报价。流量来源主要靠sdk对接的第三方媒体和api对接的厂商流量，主要涉及的开发有安卓前端sdk技术和广告检索技术。平台能力现在支持ctr、cvr、deepcvr预估，rta，dpa，利润率控制，adx流量分发等。
请你构造一些符合实际情况的具有程序化广告问题的咨询者和专家的连续多轮对话记录。
要求咨询者作为{job_description}角色，围绕{core_technology}基础知识提出问题，并且勇于追问。专家的回复尽可能包含程序化广告的专业知识，并且考虑咨询者的理解能力。注意，构造的数据必须以专家的陈述为结束语，请只返回完整的对话内容。请以如下格式返回生成的数据：
咨询者：咨询者的咨询或陈述 
专家：专家的追问和建议'''
        
        message_id = self.create_task(prompt)
        if message_id:
            result = self.get_result(message_id)
            print(f"对话生成完成，长度: {len(result) if result else 0}")
            return result
        return None

def save_jsonl(data_lis, file_path):
    import json
    with open(file_path, 'at', encoding='utf-8') as file:
        for item in data_lis:
            json_string = json.dumps(item, ensure_ascii=False) + '\n'
            file.write(json_string)

if __name__ == '__main__':
    idx = 0
    parser = argparse.ArgumentParser(description='数据生成参数')
    parser.add_argument('--data', type=str, default='zhihu_conversation', help='输出文件名')
    args = parser.parse_args()

    # 从配置文件读取角色和技术
    with open('config.yml', 'r', encoding='utf-8') as f:
        configs = yaml.load(f.read(), Loader=yaml.FullLoader)

    job_dict = configs['job_description']
    job_description = list(job_dict.keys())
    job_description_w = list(job_dict.values())
    
    tech_dict = configs['core_technology']
    core_technology = list(tech_dict.keys())
    core_technology_w = list(tech_dict.values())

    conversation_lis = []
    zhihu = ZhihuDirectAnswer()

    for i in tqdm(range(10)):
        one_conversation = {
            "conversation": []
        }

        # 随机选择角色和技术
        job = random.choices(job_description, job_description_w, k=1)[0]
        ct = random.choices(core_technology, core_technology_w, k=1)[0]
        
        # 生成对话
        res = zhihu.generate_conversation(job, ct)
        if not res:
            print(f"第 {i+1} 次生成失败，跳过")
            continue

        # 解析对话
        doctor_pattern = r'专家：(.*?)(咨询者：|$)'
        doctor_matches = re.findall(doctor_pattern, res, re.DOTALL)
        doctor_conversations = [match[0] for match in doctor_matches]

        patient_pattern = r'咨询者：(.*?)专家：'
        patient_matches = re.findall(patient_pattern, res, re.DOTALL)
        patient_conversations = [match for match in patient_matches]

        # 构造对话格式
        for doc, pat in zip(doctor_conversations, patient_conversations):
            if len(one_conversation['conversation']) == 0:
                one_conversation['conversation'].append(
                    {
                        "system": "现在你是一个资深程序化广告专家，我有一些问题，请你用专业的知识帮我解决。",
                        "input": pat.strip(),
                        "output": doc.strip()
                    }
                )
            else:
                one_conversation['conversation'].append(
                    {
                        "input": pat.strip(),
                        "output": doc.strip()
                    }
                )

        conversation_lis.append(one_conversation)
        idx += 1

        # 每生成10条数据存储一次
        if (idx % 1 == 0):
            path = f'./output/data_{args.data}_{idx // 10}.jsonl'
            save_jsonl(data_lis=conversation_lis, file_path=path)
            conversation_lis = []  # 清空
        
        time.sleep(60)