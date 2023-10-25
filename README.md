# hydro_privatedata
Data processing for various databases, sheet files, etc. in our own servers

目前暂拟分为两个部分：请求与上传数据库的API封装，以及各种形式数据表格的标准化，使之符合关系型数据库第二范式（2NF）或第三范式（3NF）。

请求与上传数据库的API封装方面，应满足如下原则：

1.尽量不编写原生SQL语句，而是通过API封装后方法读取服务器上的数据表格；

2.一定不能覆盖原始数据，需要显式指定数据下载与上传路径；

数据标准化是指：现有的很多项目，雨水情数据并不符合标准，例如桓仁水库的列名并不是具体的日期、雨量等指标，而是年份，表头与数据不对应，甚至不满足第一范式（1NF）；
碧流河项目的历史数据分为多个excel工作表，只有第一张表具有表头，其他工作表均无，也不满足1NF。

因此，需要改变不同项目的数据库表结构，使之符合数据库三范式，以便整理储存。

参考书目：《数据库系统概念》第六版
