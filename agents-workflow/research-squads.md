# research agent team 工作流设计

## Roles

- **Orchestrator**:
  - 作为项目的统筹规划核心，整体项目的推进都是由 orchestrator 完成的，所有 worker 在完成任务之后都需要告知 orchestrator 任务完成情况
  - Orchestrator 要做什么：
    - 指定 Planner 去获取项目简介，完成项目 issues 设计
    - 统筹 issues 执行路径
    - 执行 research agents 完成研究工作，并接收其完成信号
    - 协调 adversarial agents 进行质量检查
    - 协调 research agents 和 adversarial agents 之间的对抗 audit/revise， 让他们达成共识，确保研究工作的质量
    - 当所有研究工作完成后，告知 Technical Writer，并让其完成最后的报告产出
- **Project Planner**:
  - 作为项目的 issue 设计 worker，只需要在项目开始阶段完成项目 issue 的设计和规划
  - Project Planner 要做什么：
    - 完成项目的 issue 设计和 block 关系规划，帮助 orchestrator 统筹 issues 执行路径
- **Research Agent**:
  - 作为项目的研究 worker，需要完成研究工作，然后将所有的研究工作 output 在 github repo 中完成持久化
  - Research Agent 要做什么：
    - 完成研究工作，然后告诉 orchestrator 完成情况
    - 借助 orchestrator 的协调，完成和 Adversarial Agent 之间的对抗性交流，确保研究结果的质量
    - 达成一致后，可视为完成研究工作，然后需要做：
      - 将研究结果在当前 issue 中以 comment 的形式输出
      - 将研究结果在 github repo 中完成持久化
      - 通知 orchestrator，然后 orchestrator 将研究结果简介和 output 的 github url 在 Technical Writer 所属的那个 issue 中以 comment 的形式保留记录，作为 Technical Writer 最后工作的上下文
- **Adversarial Agent**:
  - 作为项目的 adversarial worker，需要对 research agent 的工作进行质量检查，确保无误
  - Adversarial Agent 要做什么：
    - 对 research agent 的工作进行质量检查，确保无误
- **Technical Writer**:
  - 作为项目的技术文档编写 worker，需要将 research agent 的所有工作进行汇总并输出一份优秀的研究报告
  - Technical Writer 要做什么：
    - 将 research agent 的所有工作进行汇总并输出一份优秀的研究报告

## Workflow

1. 组建一个 agent teams/squad，然后指定 orchestrator agent 是 leader，我需要 orchestrator 去获取整个项目的简介（description），然后进行工作的分配
2. orchestrator 指定 Project Planner 去根据项目 description 进行项目的 issue 设计和规划（由于 issue 是未来其他 agents 工作的关键 context，所以需要有一定的标准，一定要写得好），然后任务完成后 Planner 需要告知 orchestrator 项目的 issue 设计和规划结果
3. orchestrator 需要查看项目 issues 的规划情况，然后根据规划结果进行工作的分配，在这里需要注意可并行性，尽可能多的（但是不要太多，我觉得 5 个并行最多了）进行工作执行
4. research agents 执行具体的工作任务（并完成 Github Repo 上的持久化），并在 orchestrator 的帮助下和 adversarial agents 一起优化研究报告质量，达成一致后需要告知 orchestrator 任务完成情况（告诉它在 github repo 的那个文件里面），同时这个信息也需要在 Technical Writer 最后完成研究报告的 issue 中保留记录，因为 Technical Writer 需要在最后完成研究报告的输出
5. 当研究任务全部完成后，orchestrator 会通知 Technical Writer Agent 完成研究报告的输出，并将最终的报告落盘到 github repo

## 注意点

1. 我希望 Planner 能够给 Technical Writer Agent 专门留一个 issue 完成最后的报告输出，然后我希望每次 research agent 在完成一个 issue 后（将这个 issue 的状态设置为 done 的时候）会在这个专门留给 Technical Writer 最后写报告的 issue 里面 comment，说明一下 research agent 完成的这个 issue 的基本内容以及 output 的情况（比如是 github repo 的什么位置/url），这样这个 issue 就可以作为最后 Technical Writer 汇总报告的时候的重要上下文了
2. 我希望所有的 worker 和 orchestrator 通信的手段是通过显式的方式（比如在 issue 里面 comment/@对方），如果 orchestrator 收到了这个信息，就可以通过点击 emoji 的方式来告知已收到（主要是为了让人看到整个交流的过程）
3. research agent 和 adversarial agents 之间的交互采用两阶段流程：Phase A 中 research agent 使用 `/research-outline` 生成并持久化 outline，然后告知 orchestrator；orchestrator 唤起 adversarial agent 使用 `/research-review` 审查 outline，并只输出具体 patch 建议和 recommendation，由 orchestrator 决定是否让 research agent 修订或进入 Phase B。Phase B 中 research agent 使用 `/research-deep-output` 生成并持久化 draft，adversarial agent 只审查已落盘的 draft artifact；只有 adversarial approve 或 orchestrator 明确 `accept-risk` 后，research agent 才能把 accepted draft 提升到 final path。
4. 关于研究报告中的 diagrams，我希望你可以尽可能精准的进行图示，然后在 research agent 工作阶段使用 mermaid 或者 ASCII 的方式画图。在 Technical Writer 阶段，**选择性升级**：只有架构图/系统拓扑图/组件依赖图使用 `/fireworks-tech-graph` 升级，流程图/序列图/状态图保留 Mermaid（因为 Mermaid 对这些类型的渲染已经足够好且易于维护），ASCII 图至少升级为 Mermaid。如果 `/fireworks-tech-graph` 不可用则全部使用 Mermaid 并记录为 M1 集成缺口。

## 未来扩展
1. 是否需要一个专门的 code analysis agent 来做专门的 codebase 分析，因为有一些工具是可以帮助做代码分析的，比如 https://github.com/tirth8205/code-review-graph
2. 是否需要对 Planner 的工作也有一个 review agent，因为他的工作质量高低直接影响了后续的结果
