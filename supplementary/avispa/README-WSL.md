# AVISPA/WSL 复现说明

已在 Ubuntu 22.04.5（WSL2）中安装并验证：

- 官方 `hlpsl2if` 2.1（安装在 `/opt/avispa/bin/hlpsl2if`，并链接到 `/usr/local/bin/hlpsl2if`）；
- OFMC 2020 Linux 后端（安装在 `/opt/avispa/bin/ofmc`，并链接到 `/usr/local/bin/ofmc`）；
- `libc6:i386`、`libncurses5:i386`、`libtinfo5:i386` 等 HLPSL2IF 兼容库；
- `libffi6`、`libgmp10` 等 OFMC 运行库；
- CL-AtSe 使用 Docker Desktop 中的 `turuani/cl-atse:latest` 镜像从 WSL 调用。

## 运行

在 WSL Ubuntu 中执行：

```bash
MODEL=/mnt/e/Work/认证论文/彭博论文/MDPI_template_ACS/els-cas-templates/els-cas-templates/TSP_template/avispa/tsp_cmc_core.hlpsl
IF=/tmp/tsp_cmc_core.if
hlpsl2if --stdout "$MODEL" > "$IF"
ofmc --classic --depth 10 "$IF"
```

CL-AtSe 需要将 `IF` 放入一个只含该文件的目录后，通过 Docker Desktop 调用：

```bash
docker run --rm -v /path/to/dedicated-run-dir:/run:ro \
  turuani/cl-atse:latest --if --free /run/tsp_cmc_core.if
```

## 结果与边界

论文所引用的最新 SPAN/AVISPA 报告见本目录的 `avispa.pdf`。在有界会话、类型化模型和所声明目标下，OFMC 与 CL-AtSe 均报告 `SAFE`（OFMC：4 个访问节点、深度 3；CL-AtSe：分析 8 个状态、可达 3 个状态）。

早期 WSL 运行的文本输出可能显示 `NO_ATTACK_FOUND`；该字符串表示在给定搜索界限内未发现攻击，不替代最新报告中的 `SAFE` 结论。

该模型抽象了论文中的 M1--M4 核心认证/密钥协商消息，并将密码、智能卡、
生物特征和 CEAF 抽象为共享秘密；模型明确不覆盖 TEE 提取、在线限流、离线
枚举、两记录恢复窗口以及 M5--M6 更新确认。因此结果应表述为“在所声明的
有界模型与假设下未发现攻击”，不能表述为对完整实现的无条件证明。
