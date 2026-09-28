# 具身智能安全工具箱

Feiyang Song 维护的个人研究作品，基于 Northwestern IDEAS Lab 的 SENTINEL 团队评估模块，补充独立运行流程与工程工具。

## 它做什么

把“安全要求 → 场景生成 → 动作和状态记录 → 规则检查 → 违规定位”串起来。六类场景包含微波炉、炉灶和淋浴环境。每类都有安全对照和故意触发违规的样例，避免只验证一个方向。

```bash
python -m pip install -r requirements.txt
python -m unittest discover -s tests -v
python -m pipeline --output outputs/demo --seed 7 --variants 2
```

打开 `outputs/demo/report.html` 查看报告。默认 24 条合成轨迹，12 条安全对照、12 条违规样例，全部符合预期；23 项测试通过。它们验证软件行为，不是模型安全率。

## 研究与实现范围

团队论文涵盖语义、规划、轨迹三个层次。当前可运行部分聚焦场景与轨迹评估：规则目录、生成器、控制器记录接口、检查器及报告。自然语言规则翻译、完整规划验证、在线模拟器实验的状态见 [架构说明](docs/ARCHITECTURE.md)。没有实现的部分不会以空函数冒充已完成。

原始评估代码保留团队署名和许可证。本次新增的生成、验证、运行与文档工作见 [来源说明](PROVENANCE.md)。项目不是整篇论文的独立个人复现。
