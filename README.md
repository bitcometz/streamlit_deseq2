需要安装stream，R，R中的DESeq2的包，
尽量不要在python中调用R的程序，会线程不可控制报错的问题

## 这个App的基础功能：
 * DESeq2.py, 主要是实现文件输入输出和画图，核心的计算是调研了DESeq2的R程序
 * DESeq2.r, 主要是计算差异表达
### 输入
 * gene.csv, 基因表达矩阵
 * meta.csv, 样品分组信息
 * res.csv, 输出文件
### 启动方式
 
streamlit run --server.port 8501 DESeq2.py
