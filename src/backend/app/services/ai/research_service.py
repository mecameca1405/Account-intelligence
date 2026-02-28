from ...db.database import sessionLocal
from ...models.analysis import Analysis

class ResearchService:

    def __init__(self, task=None):
        self.task = task

    async def execute(self, analysis_id: int):

        async with sessionLocal() as db:

            analysis = await db.get(Analysis, analysis_id)
            analysis.status = "researching"
            await db.commit()

            if self.task:
                self.task.update_state(
                    state="PROGRESS",
                    meta={"progress": 25}
                )

            # --- Tavily call ---
            
            if self.task:
                self.task.update_state(
                    state="PROGRESS",
                    meta={"progress": 50}
                )

            # --- Embeddings ---

            if self.task:
                self.task.update_state(
                    state="PROGRESS",
                    meta={"progress": 80}
                )

            analysis.status = "research_completed"
            await db.commit()

            if self.task:
                self.task.update_state(
                    state="SUCCESS",
                    meta={"progress": 100}
                )