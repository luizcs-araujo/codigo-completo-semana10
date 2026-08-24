import json
from langchain_core.language_models.fake_chat_models import FakeMessagesListChatModel
from langchain_core.messages import AIMessage

from supportops.agent import build_agent
from supportops.rag.embeddings import HashEmbeddings
from supportops.rag.service import RagService
from supportops.rag_tools import set_rag_service


class ScriptedToolModel(FakeMessagesListChatModel):
    def bind_tools(self, tools, *, tool_choice=None, **kwargs):
        return self


def call(name, args, call_id):
    return AIMessage(content="", tool_calls=[{"name":name,"args":args,"id":call_id,"type":"tool_call"}])


def test_agent_executes_tools_and_returns_structured_diagnosis():
    set_rag_service(RagService(embeddings=HashEmbeddings()))
    responses = [
        call("get_ticket_context", {"ticket_id":"TCK-4821"}, "c1"),
        call("get_user_access", {"user_id":"USR-100","resource":"dashboard:analytics"}, "c2"),
        call("get_service_health", {"service_id":"analytics-api"}, "c3"),
        call("search_technical_docs", {"query":"403 após mudança de role e cache","service_id":"analytics-api","environment":"prod","top_k":4}, "c4"),
        call("TicketDiagnosis", {
            "ticket_id":"TCK-4821","status":"needs_human","probable_cause":"cache de permissões divergente","confidence":"high",
            "evidence":[{"claim":"runbook exige invalidação direcionada com aprovação","source":"analytics-api/runbook_permission_cache_v2.md#Mitigação","version":"2.1","excerpt":"A invalidação é ação de escrita e exige aprovação humana"}],
            "retrieval_queries":["403 após mudança de role e cache"],"next_steps":["solicitar aprovação do on-call"],
            "requires_human":True,"stop_reason":"needs_write_action"
        }, "c5"),
    ]
    model = ScriptedToolModel(responses=responses)
    agent = build_agent(model=model, middleware=[])
    result = agent.invoke({"messages":[{"role":"user","content":"Investigue TCK-4821"}]})
    assert result["structured_response"].status == "needs_human"
    names = [call["name"] for msg in result["messages"] if isinstance(msg, AIMessage) for call in msg.tool_calls]
    assert names[:4] == ["get_ticket_context","get_user_access","get_service_health","search_technical_docs"]
