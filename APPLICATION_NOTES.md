# 项目展示与申请描述

推荐项目名称：**Embodied Agent Safety: Trajectory Evaluation**

角色可写：**Graduate Researcher — Team Project**

这个项目可以放在你与 Qi Zhu 教授团队的研究经历下面，作为可运行的作品样例。重点放在研究问题、流程和你实际做过的工程工作，不需要把标题写成“写了几个 case”。

## Work Samples 描述

> A standalone portfolio edition of the trajectory-evaluation subsystem from our collaborative embodied-agent safety research at Northwestern. It converts simulator metadata into symbolic predicates, checks safety rules against recorded traces, and reports violations with step-level evidence. I contributed safety-scenario generation and setup fixes in the team project and prepared this edition with a batch evaluation interface, input validation, regression tests, and reproducible examples.

这段区分了历史研究贡献与本次整理。后续如果补上你真实的运行日志和实验结果，可以进一步写具体场景、模型和结果；现有四个样例只说明代码行为。

## 面试时的讲法

可以按下面的顺序说：

1. 团队研究具身智能体执行任务时的物理安全问题。
2. 系统先把模拟器的状态与动作转成明确的逻辑条件，再用安全规则检查轨迹。
3. 你参与场景生成、初始化和测试调试；模板能按不同物体和场景生成测试实例。
4. 这个作品样例提取了团队的评估模块，补齐独立运行、错误诊断、违反规则的位置和回归测试。

英文口语版：

> Our team studies safety in embodied agents. We turn simulator observations and actions into symbolic conditions, then check them against safety rules. My work has included building safety scenarios and fixing scene setup issues. For this portfolio version, I packaged the team's evaluation module so it can run on saved traces and show which rule was violated and where.

## 当前展示状态

- 使用真实团队源码提取的评估模块，保留来源与许可证。
- 15 项测试已通过；四个合成样例中两个通过、两个检测到预期违规。
- 尚未使用你原来的本地运行日志重放，不能写真实模型的安全率或论文指标。
- 当前为本地文件，尚未建立公开仓库链接。
- 简历定稿和申请表未改动，未提交申请。
