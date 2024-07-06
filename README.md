## 测试SparkApi

### 安装依赖

进入项目根目录

```shell
pip install -r requirements.txt
```

### 设置配置

补充config.example.json文件，将其重命名为config.json

### 运行


```shell
cd src
python test_spark.py
```

## 其他库

### utils
注意，导入这个包时，直接运行的脚本文件要和utils平级或者在其之上
- Logger: 日志工具

### spark
- SparkApi: SparkLLM接口