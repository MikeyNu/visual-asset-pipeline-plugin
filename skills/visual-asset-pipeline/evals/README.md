# Agent evaluation suite

`scenarios.json` defines 20 cases across normal frontend work, source fidelity, native
output limitations, local/GitHub delivery, negative activation, and adversarial inputs.
They are **defined, not run** as live multi-model evaluations in this package.

For a proper evaluation, supply the fixture/repository/reference named by the case,
provide the intended authorized tools, and run the same task with and without the skill.
Keep model, tool access, budget, references, and environment equivalent. Preserve actual
transcripts, generated file hashes, destination evidence, screenshots, and blockers.
Never invent an image output just to make an evaluation look complete.

Score each required behavior as evidenced, missing, or not applicable with a reason.
Any hard failure fails that case. Separately score visual-purpose fit, composition,
reference fidelity, frontend correctness, safe transfer, and truthful reporting. A
numerical score should link to evidence and must not replace actual pixel inspection.

Compare results across repeated runs before claiming improved success rates. A no-skill
baseline, live native generation, paid API, remote-machine write, and artistic benchmark
are all separate experiments. None is established by the deterministic unit test suite.

See `TEST_REPORT.md` for the tests actually executed in this session.
