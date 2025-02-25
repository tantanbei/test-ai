import numpy as np
d = 64                           # 向量维度
nb = 100000                      # 数据库大小（向量数量）
nq = 10000                       # 查询数量
np.random.seed(1234)             # 设置随机种子，确保结果可复现

# 生成随机数据
xb = np.random.random((nb, d)).astype('float32')    # 生成数据库向量
xb[:, 0] += np.arange(nb) / 1000.                   # 给第一维添加一个小的线性增长
xq = np.random.random((nq, d)).astype('float32')    # 生成查询向量
xq[:, 0] += np.arange(nq) / 1000.                   # 给第一维添加一个小的线性增长

import faiss
index = faiss.IndexFlatL2(d)   # 创建使用L2距离的索引
print(index.is_trained)        # 检查索引是否需要训练（对于简单的IndexFlatL2不需要）
index.add(xb)                  # 将向量添加到索引中
D, I = index.search(xq, k=4)   # 对每个查询向量搜索4个最近邻
print(I[:5])                   # 打印前5个查询的结果   