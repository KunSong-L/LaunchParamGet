#!/usr/bin/python3
# 自动解析ros launch文件中传递到参数服务器中的参数
import os
from ruamel import yaml
import rospkg
import re


def is_number(s):
    try:
        float(s)
        return True
    except ValueError:
        pass
 
    try:
        import unicodedata
        unicodedata.numeric(s)
        return True
    except (TypeError, ValueError):
        pass
 
    return False


def LoadYamlFile(path):
    file = open(path)
    tmp = yaml.load(file,Loader=yaml.Loader)
    return tmp



def dictCompare(common:dict,add:dict):
    common_new = common.copy()
    add_new = add.copy()
    for now_keys_common in common.keys():
        if not now_keys_common in add_new.keys():
            common_new.pop(now_keys_common)
        else:
            if common_new[now_keys_common] == add_new[now_keys_common]:
                add_new.pop(now_keys_common)
            else:
                if isinstance(common_new[now_keys_common],dict) and isinstance(add_new[now_keys_common],dict):
                    tmp1,tmp2 = dictCompare(common_new[now_keys_common],add_new[now_keys_common])
                    common_new[now_keys_common] = tmp1.copy()
                    add_new[now_keys_common] = tmp2.copy()
                else:
                    common_new.pop(now_keys_common)
    
    return common_new,add_new


def LaunchParamGet(input_path,output_file_name):
    rospack = rospkg.RosPack()
    name_file= os.listdir(input_path) #得到文件夹下的所有文件名称
    data = {}

    for now_file in name_file: #遍历文件夹内所有文件
        if now_file.split('.')[-1] != 'launch': continue
        file = open(input_path+now_file)
        print('now collecting file is:   ' + input_path+now_file)
        tmp = {}
        count = 0
        file_data = file.readlines()
        for now_line in file_data: # read the file
            now_line = now_line.strip() #delete space and tab in the beginning and end
            now_line = now_line.replace(' ','') # delete all space

            if '<rosparam' in now_line: # 由rosparam定义的，分为load file和直接定义
                # print(now_line)
                if 'command="load"' in now_line and '$(env' not in now_line and '$(arg' not in now_line: # 直接定义路径
                    YamlFile = re.findall('=\"(.*?)\"', now_line)[1]
                    # print(package_path + YamlFile)
                    tmp = {**tmp,**LoadYamlFile(YamlFile)} # 融合两个字典
                if 'command="load"' in now_line and 'find' in now_line and '$(env' not in now_line and '$(arg' not in now_line: # 由find定义路径
                    #解决<rosparam command="load" file="$(find 
                    PackageNameBegin = now_line.find('find') + 4
                    PackageNameEnd = now_line.find(')/')
                    PackageName = now_line[PackageNameBegin:PackageNameEnd]
                    package_path = rospack.get_path(PackageName)

                    YamlFileBegin = now_line.find(')/') + 1
                    YamlFileEnd = now_line.find('.yaml') + 5
                    YamlFile = now_line[YamlFileBegin:YamlFileEnd]

                    # print(package_path + YamlFile)

                    tmp = {**tmp,**LoadYamlFile(package_path + YamlFile)} # 融合两个字典
                if 'param="' in now_line:
                    #解决在rosparam直接定义的
                    param = re.findall('param="(.*?)"',now_line)[0]
                    if not re.findall('>(.*?)<',now_line): #定义在下一行
                        value = ''
                        i = 1
                        while True:
                            next_line = file_data[count + i]
                            if '</rosparam>' in next_line : break
                            next_line = next_line.strip()
                            value = value + next_line
                            i += 1
                        if '$(arg' in value:
                            count += 1 
                            continue
                        if value == 'true' or value == 'false': # upper
                            value = value.capitalize()
                        if '[' in value or 'True' in value or 'False' in value or is_number(value):
                            tmp[param] = eval(value)
                        else:
                            tmp[param] = value
                    else:
                        value = re.findall('>(.*?)<',now_line)[0]
                        if '$(arg' in value:
                            count += 1 
                            continue
                        if value == 'true' or value == 'false':
                            value = value.capitalize()
                        if '[' in value or 'True' in value or 'False' in value or is_number(value):
                            tmp[param] = eval(value)
                        else:
                            tmp[param] = value


            if '<param' in now_line: #由param直接定义的
                param = re.findall('\"(.*?)\"', now_line)[0]
                if '$(find' in now_line:#包路径
                    target_package = re.findall('find(.*?)[)]',now_line)[0]
                    package_path = rospack.get_path(target_package)
                    tmp[param] = package_path
                if '$' not in now_line:#直接定义的
                    value = re.findall('value="(.*?)"/',now_line)[0]
                    if '$(arg' in value:
                        count += 1 
                        continue
                    if value == 'true' or value == 'false':
                        value = value.capitalize()
                    if '[' in value or 'True' in value or 'False' in value or is_number(value):
                        tmp[param] = eval(value)
                    else:
                        tmp[param] = value 

                # print(param)

            count = count +1    

        now_name = now_file.rstrip('.launch')
        data[now_name] = tmp
        


    curpath = os.path.dirname(os.path.realpath(__file__))
    WriteYamlPath = os.path.join(curpath, output_file_name)

    # 写入到yaml文件
    with open(WriteYamlPath, "w", encoding="utf-8") as f:
        yaml.dump(data, f, Dumper=yaml.RoundTripDumper)
    


input_path = './'
output_file_name = 'test.yaml'

LaunchParamGet(input_path,output_file_name)


