import matplotlib.pyplot as plt
import numpy as np

# 假定有20次信号
n = 20
returns = np.random.normal(0.02, 0.05, n)  # 模拟收益，正负都有
plt.figure(figsize=(10, 5))
plt.scatter(range(n), returns, c=returns, cmap='RdYlGn', s=80, edgecolor='k')
plt.axhline(0, color='gray', linestyle='--', lw=1)
plt.title('Trade Return Distribution by Signal Index')
plt.xlabel('Signal Index')
plt.ylabel('Trade Return')
plt.colorbar(label='Return')
plt.show()
