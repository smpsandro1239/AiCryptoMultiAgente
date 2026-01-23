from multiagent_trading.agents.base import BaseAgent
import asyncio

class GovernanceAgent(BaseAgent):
    """
    Agente responsável pela governação do sistema.
    Gere votações para alteração de parâmetros globais (taxas, limites, etc.).
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.proposals = {} # {proposal_id: {votes: [], status: 'OPEN'}}
        self.event_bus.subscribe("governance_proposal", self.on_proposal)
        self.event_bus.subscribe("governance_vote", self.on_vote)

    async def on_proposal(self, data):
        prop_id = data.get("id")
        self.proposals[prop_id] = {
            "description": data.get("description"),
            "target_param": data.get("param"),
            "target_value": data.get("value"),
            "votes": [],
            "status": "OPEN"
        }
        self.logger.info(f"Nova proposta de governação: {data.get('description')}")

    async def on_vote(self, data):
        prop_id = data.get("id")
        if prop_id in self.proposals and self.proposals[prop_id]["status"] == "OPEN":
            self.proposals[prop_id]["votes"].append(data.get("agent_name"))

            # Se atingir quórum (ex: 3 votos)
            if len(self.proposals[prop_id]["votes"]) >= 3:
                await self._execute_proposal(prop_id)

    async def _execute_proposal(self, prop_id):
        prop = self.proposals[prop_id]
        prop["status"] = "APPROVED"
        self.logger.success(f"Proposta {prop_id} aprovada e executada: {prop['target_param']} -> {prop['target_value']}")

        # Publicar alteração global
        await self.event_bus.publish("parameter_changed", {
            "param": prop["target_param"],
            "value": prop["target_value"]
        })
