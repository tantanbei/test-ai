import json
import random
import argparse
import yaml 
import re

from tqdm import tqdm

with open('config.yml', 'r', encoding='utf-8') as f:
    configs = yaml.load(f.read(), Loader=yaml.FullLoader)

def qwen_api(model_name, job_description, core_technology):
    import dashscope
    from http import HTTPStatus

    dashscope.api_key = configs['dashscope_api_key']
    # prompt = f'''你是一个研究过无数具有心理健康问题的病人与心理健康医生对话的专家，请你构造一些符合实际情况的具有心理健
    # 康问题的病人和心理健康医生的连续的多轮对话记录。要求病人的问题属于{data}场景，具有{emo}情感，医生的回复尽可能包含心理辅导知识，并且能够一步步诱导病人说出自己的问题进而提供解决问题的可行方案。注意，构造的数据必须以医生的陈述为结束语，请只返回完整的对话内容。请以如下格式返回生成的数据：
    # 病人：病人的咨询或陈述 
    # 医生：医生的安抚和建议
    # '''
    prompt = f'''你现在是一个资深程序化广告专家，现任职于一家广告平台公司，核心目标是保证广告平台利益最大。
程序化广告公司简介：预算来源分为两部分，一部分来自开户平台，客户由销售洽谈接入进来，目前主要客户有百度系、阿里系、头条系等，客户投放方式主要依赖ocpm，主要预算考核目标有首次拉活、激活、次留等，有少量cpm和cpc出价预算，定向方式有性别、年龄、人群包、时段、rta等，主要涉及的开发有广告算法、广告检索技术和广告平台技术。另一部分预算来自于dsp，dsp由商务引入，广告检索技术负责对接开发，dsp都是rtb报价。流量来源主要靠sdk对接的第三方媒体和api对接的厂商流量，主要涉及的开发有安卓前端sdk技术和广告检索技术。平台能力现在支持ctr、cvr、deepcvr预估，rta，dpa，利润率控制，adx流量分发等。
请你构造一些符合实际情况的具有程序化广告问题的咨询者和专家的连续多轮对话记录。
要求咨询者作为{job_description}角色，围绕{core_technology}基础知识提出问题，并且勇于追问。专家的回复尽可能包含程序化广告的专业知识，并且考虑咨询者的理解能力。注意，构造的数据必须以专家的陈述为结束语，请只返回完整的对话内容。请以如下格式返回生成的数据：
咨询者：咨询者的咨询或陈述 
专家：专家的追问和建议
    '''
    response = dashscope.Generation.call(
        model=model_name,
        prompt=prompt,
        history=[],
    )

    if response.status_code == HTTPStatus.OK:
        if model_name.startswith('deepseek'):
            result = response.output.choices[0].message.content
        else:
            result = response.output.text
        print(result)
    else:
        result = 'ERROR'
    return result


def save_jsonl(data_lis, file_path):
    import json

    # 将字典列表写入文件，每一行一个字典
    with open(file_path, 'at', encoding='utf-8') as file:
        for item in data_lis:
            json_string = json.dumps(item, ensure_ascii=False) + '\n'
            file.write(json_string)


if __name__ == '__main__':
    idx = 0
    parser = argparse.ArgumentParser(description='数据生成参数')

    parser.add_argument('--model', type=str, help='模型名')

    # 解析命令行参数
    args = parser.parse_args()
    model_name = args.model

    job_dict = configs['job_description']
    job_description = list(job_dict.keys())
    job_description_w = list(job_dict.values())
    
    tech_dict = configs['core_technology']
    core_technology = list(tech_dict.keys())
    core_technology_w = list(tech_dict.values())

    conversation_lis = []
    for i in tqdm(range(100)):
        one_conversation = {
            "conversation": []
        }

        dia_tuple = []
        job = random.choices(job_description, job_description_w, k=1)[0]
        ct = random.choices(core_technology, core_technology_w, k=1)[0]
        res = qwen_api(model_name, job_description=job, core_technology=ct)
        print(res)

        # 一次会话
        doctor_pattern = r'专家：(.*?)(咨询者：|$)'

        doctor_matches = re.findall(doctor_pattern, res, re.DOTALL)
        doctor_conversations = [match[0] for match in doctor_matches]

        patient_pattern = r'咨询者：(.*?)专家：'
        patient_matches = re.findall(patient_pattern, res, re.DOTALL)
        patient_conversations = [match for match in patient_matches]

        for doc, pat in zip(doctor_conversations, patient_conversations):
            if len(one_conversation['conversation']) == 0:
                one_conversation['conversation'].append(
                    {
                        "system": "现在你是一个资深程序化广告专家，我有一些问题，请你用专业的知识帮我解决。",
                        "input": pat,
                        "output": doc
                    },
                )

            else:
                one_conversation['conversation'].append(
                    {
                        "input": pat,
                        "output": doc
                    },
                )
        conversation_lis.append(one_conversation)

        idx += 1

        # 每生成10条数据存储一次
        if (idx % 10 == 0):
            path = f'./output/data_{model_name}_{idx / 10}.jsonl'
            save_jsonl(data_lis=conversation_lis, file_path=path) 
            conversation_lis = []  # 清空
