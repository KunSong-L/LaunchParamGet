# 解析ROS Launch文件生成的参数
## 用法
首先在`LaunchParamGet.py`(基于XML解析的下同，基于XML解析的方法会识别注释）的最后设置需要解析的文件目录和输出的文件名。如当前目录可以写为`'./'`，文件名可以写为`'test.txt'`（解析完成的文件自动放在当前文件夹下）。然后直接调用`LaunchParamGet.py`进行解析即可。该程序自动解析所有Launch文件产生的参数。



解析出的文件自动生成为一个YAML文件。每个Launch文件生成的参数都被包含在以其开头的key下面。



如`test.launch`文件中解析出的参数名称如下：
```yaml
test
  a:
  - 1
  - 2
  - 3
  - 4
  b: 1
  c: true
  d: false
  e: 0.1
  f: -0.1
  g: This is a YAML file.
  h:
    h1: nested
    h2: -0.1
  rosparam_test_id: 0
  param_test: true
```

如果当前文件夹下还有一个`test2.launch`，那么解析出的参数如下：
```yaml
test
  a:
  - 1
  - 2
  - 3
  - 4
  b: 1
  c: true
  d: false
  e: 0.1
  f: -0.1
  g: This is a YAML file.
  h:
    h1: nested
    h2: -0.1
  rosparam_test_id: 0
  param_test: true
test2:
  ....
```
## 目前可以解析出的参数
目前可以解析出的参数如下：
* \<rosparam command="load" file="test_yaml.yaml" />：由rosparam通过loadfile定义的
* 上述各式中包含file=$(find rospkg)的
* \<rosparam param="rosparam_test_id">0</rosparam>：直接定义的，包括分行书写
* \<param name="param_test" value="true"/>：利用param格式定义的
