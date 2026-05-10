import uuid
from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task, before_kickoff, after_kickoff
from crewai.agents.agent_builder.base_agent import BaseAgent
from .tools.scanner_tool import SCCScannerTool
from .tools.enrichment_tool import EnrichmentTool
from .observability import get_logger, log_event, increment
from .observability import RUNS_STARTED, RUNS_COMPLETED, RUNS_FAILED, TOOL_CALLS_TOTAL
from .schemas.finding_list import FindingList
from .schemas.enriched_finding_list import EnrichedFindingList
from .schemas.scored_finding_list import ScoredFindingList
from .schemas.security_report import SecurityReport

_logger = get_logger("crew")


@CrewBase
class GcpSecurityIntelligence():
    """GcpSecurityIntelligence crew"""

    agents: list[BaseAgent]
    tasks: list[Task]
    _trace_id: str = ""
    _project_id: str = ""

    @before_kickoff
    def on_start(self, inputs: dict) -> dict:
        """Generate trace ID and emit run_started log and metric."""
        self._trace_id = str(uuid.uuid4())
        self._project_id = inputs.get("project_id", "unknown")
        log_event(_logger, self._trace_id, "crew", "run_started", project_id=self._project_id)
        increment(RUNS_STARTED, self._project_id)
        return inputs

    @after_kickoff
    def on_finish(self, output):
        """Emit run_completed log and metric."""
        log_event(_logger, self._trace_id, "crew", "run_completed", project_id=self._project_id)
        increment(RUNS_COMPLETED, self._project_id)
        return output

    def _on_task_complete(self, output) -> None:
        """Log task completion with agent name and trace ID."""
        agent_name = getattr(output, "agent", "unknown")
        log_event(_logger, self._trace_id, agent_name, "task_completed", project_id=self._project_id)

    def _on_step(self, step_output) -> None:
        """Log each agent step and increment tool_calls_total when a tool was used."""
        tool_used = getattr(step_output, "tool", None)
        if tool_used:
            log_event(
                _logger, self._trace_id, "agent", "tool_call",
                tool=tool_used,
                project_id=self._project_id,
            )
            increment(TOOL_CALLS_TOTAL, self._project_id)

    @agent
    def scanner(self) -> Agent:
        """Return the SCC scanner agent with its scanning tool."""
        return Agent(
            config=self.agents_config['scanner'],
            verbose=True,
            tools=[SCCScannerTool()]
        )

    @agent
    def enrichment(self) -> Agent:
        """Return the enrichment agent with its GCP enrichment tool."""
        return Agent(
            config=self.agents_config['enrichment'],
            verbose=True,
            tools=[EnrichmentTool()],
        )

    @agent
    def risk_analyst(self) -> Agent:
        """Return the risk analyst agent."""
        return Agent(
            config=self.agents_config['risk_analyst'],
            verbose=True
        )

    @agent
    def reporter(self) -> Agent:
        """Return the reporter agent."""
        return Agent(
            config=self.agents_config['reporter'],
            verbose=True
        )

    @task
    def scanner_task(self) -> Task:
        """Return the scanner task."""
        return Task(
            config=self.tasks_config['scanner_task'],
            output_pydantic=FindingList,
            callback=self._on_task_complete,
        )

    @task
    def enrichment_task(self) -> Task:
        """Return the enrichment task."""
        return Task(
            config=self.tasks_config['enrichment_task'],
            output_pydantic=EnrichedFindingList,
            callback=self._on_task_complete,
        )

    @task
    def risk_analysis_task(self) -> Task:
        """Return the risk analysis task."""
        return Task(
            config=self.tasks_config['risk_analysis_task'],
            output_pydantic=ScoredFindingList,
            callback=self._on_task_complete,
        )

    @task
    def reporter_task(self) -> Task:
        """Return the reporter task."""
        return Task(
            config=self.tasks_config['reporter_task'],
            output_pydantic=SecurityReport,
            output_file='report.md',
            callback=self._on_task_complete,
        )

    @crew
    def crew(self) -> Crew:
        """Assemble the GcpSecurityIntelligence crew with observability callbacks."""
        return Crew(
            agents=self.agents,
            tasks=self.tasks,
            process=Process.sequential,
            verbose=True,
            step_callback=self._on_step,
            task_callback=self._on_task_complete,
        )
