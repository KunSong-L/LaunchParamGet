#!/usr/bin/python3
import os
from ruamel import yaml
import rospkg
import re
import xml.etree.ElementTree as ET

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
        tree = ET.parse(now_file)
        root = tree.getroot()
        print('now collecting file is:   ' + input_path+now_file)
        tmp = {}

        
        for child in root:
            if child.tag == 'node':
                node_root = child
            else:
                continue


        for child_param in node_root:
            print(child_param.tag,child_param.attrib)
            commad_dic = child_param.attrib
            if child_param.tag == 'rosparam':
                if 'command' in commad_dic.keys() and commad_dic['command'] == 'load':
                    yaml_file = commad_dic['file']
                    if '$(env' in yaml_file or '$(arg' in yaml_file:continue
                    if 'find' not in yaml_file: # 直接定义路径
                        YamlFile = yaml_file
                        # print(package_path + YamlFile)

                        tmp = {**tmp,**LoadYamlFile(YamlFile)} # 融合两个字典
                    else:
                        now_line = commad_dic['file']
                        PackageNameBegin = now_line.find('find') + 4
                        PackageNameEnd = now_line.find(')/')
                        PackageName = now_line[PackageNameBegin:PackageNameEnd]
                        package_path = rospack.get_path(PackageName)

                        YamlFileBegin = now_line.find(')/') + 1
                        YamlFileEnd = now_line.find('.yaml') + 5
                        YamlFile = now_line[YamlFileBegin:YamlFileEnd]

                        # print(package_path + YamlFile)

                        tmp = {**tmp,**LoadYamlFile(package_path + YamlFile)} # 融合两个字典
                if 'param' in commad_dic.keys():
                    param = commad_dic['param']
                    value = child_param.text.replace('\n','')
                    if '$(arg' in value:
                        continue
                    if value == 'true' or value == 'false': # upper
                        value = value.capitalize()
                    if '[' in value or 'True' in value or 'False' in value or is_number(value):
                        tmp[param] = eval(value)
                    else:
                        tmp[param] = value
                    
                    
            if child_param.tag == 'param':
                param = commad_dic['name']
                if 'value' in commad_dic.keys():
                    now_line = commad_dic['value']
                    now_line = now_line.replace('\n','')
                    now_line = now_line.replace(' ','')
                else:
                    now_line = child_param.text.replace('\n','')
                    now_line = now_line.replace(' ','')
                if '$(find' in now_line:#包路径
                    # 可能会有问题:find 后面还有东西
                    target_package = re.findall('find(.*?)[)]',now_line)[0]
                    package_path = rospack.get_path(target_package)
                    tmp[param] = package_path
                if '$' not in now_line:#直接定义的
                    value = now_line
                    if value == 'true' or value == 'false':
                        value = value.capitalize()
                    if '[' in value or 'True' in value or 'False' in value or is_number(value):
                        tmp[param] = eval(value)
                    else:
                        tmp[param] = value 
                                
        now_name = now_file.rstrip('.launch')
        data[now_name] = tmp
        


    curpath = os.path.dirname(os.path.realpath(__file__))
    WriteYamlPath = os.path.join(curpath, output_file_name)

    # 写入到yaml文件
    with open(WriteYamlPath, "w", encoding="utf-8") as f:
        yaml.dump(data, f, Dumper=yaml.RoundTripDumper)


input_path = './'
output_file_name = 'test2.yaml'

LaunchParamGet(input_path,output_file_name)
