from crewai import Agent, Crew, Process, Task

class FinancialAnalyzerCrew:
    def __init__(self, agents_config=None, tasks_config=None):
        # load configs if provided, else from package config
        self.agents_config = agents_config or {}
        self.tasks_config = tasks_config or {}
        # placeholders for Agent objects (framework dependent)
        self.agents = []
        self.tasks = []

    def extractor(self):
        return Agent(config=self.agents_config.get('extractor', {}), verbose=True)

    def accountant(self):
        return Agent(config=self.agents_config.get('accountant', {}), verbose=True)

    def analyst(self):
        return Agent(config=self.agents_config.get('analyst', {}), verbose=True)

    def recommender(self):
        return Agent(config=self.agents_config.get('recommender', {}), verbose=True)

    def ingest_pdf_task(self):
        return Task(config=self.tasks_config.get('ingest_pdf_task', {}), output_file='../data/extracted.json')

    def analyze_financials_task(self):
        return Task(config=self.tasks_config.get('analyze_financials_task', {}), output_file='output/metrics.json')

    def write_report_task(self):
        return Task(config=self.tasks_config.get('write_report_task', {}), output_file='output/analysis.md')

    def final_recommendation_task(self):
        return Task(config=self.tasks_config.get('final_recommendation_task', {}), output_file='output/recommendations.json')

    def crew(self):
        # This is a simplified placeholder. Adjust per CrewAI SDK.
        return Crew(agents=self.agents, tasks=self.tasks, process=Process.sequential, verbose=True)
