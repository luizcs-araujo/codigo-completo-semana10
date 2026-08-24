from pathlib import Path
from langchain_core.embeddings import DeterministicFakeEmbedding
from langchain_core.language_models.fake_chat_models import FakeMessagesListChatModel
from langchain_core.messages import AIMessage
from supportops.agent import build_agent
from supportops.rag.index import rebuild_index
from supportops.rag.service import ChromaRagService
from supportops.rag_tools import set_rag_service


class ScriptedToolModel(FakeMessagesListChatModel):
    def bind_tools(self, tools, *, tool_choice=None, **kwargs):
        return self


def call(name, args, call_id):
    return AIMessage(content="", tool_calls=[{"name":name,"args":args,"id":call_id,"type":"tool_call"}])


def test_agent_runs_tools_chroma_and_structured_output(tmp_path: Path):
    embedding = DeterministicFakeEmbedding(size=96)
    rebuild_index(embedding, tmp_path, "agent")
    set_rag_service(ChromaRagService(embedding, tmp_path, "agent"))
    responses = [
        call("get_ticket_context", {"ticket_id":"TCK-4821"}, "c1"),
        call("get_user_access", {"user_id":"USR-100","resource":"dashboard:analytics"}, "c2"),
        call("get_metric_snapshot", {"service_id":"analytics-api","environment":"prod"}, "c3"),
        call("search_technical_docs", {"query":"403 role cache","service_id":"analytics-api","environment":"prod","top_k":5}, "c4"),
        call("TicketDiagnosis", {
            "ticket_id":"TCK-4821","status":"needs_human","probable_cause":"cache de permissões divergente","confidence":"high",
            "evidence":[{"claim":"invalidação exige humano","source":"analytics-api/runbook_403_v2.md#Mitigação","version":"2.1","relevance":0.9,"excerpt":"A invalidação exige aprovação do on-call."}],
            "retrieval_queries":["403 role cache"],"next_steps":["solicitar invalidação direcionada"],"requires_human":True,"stop_reason":"needs_write_action"
        }, "c5"),
    ]
    model = ScriptedToolModel(responses=responses)
    graph = build_agent(model=model, middleware=[])
    result = graph.invoke({"messages":[{"role":"user","content":"Investigue TCK-4821"}]})
    assert result["structured_response"].status == "needs_human"
    names = [c["name"] for message in result["messages"] if isinstance(message, AIMessage) for c in message.tool_calls]
    assert names[:4] == ["get_ticket_context", "get_user_access", "get_metric_snapshot", "search_technical_docs"]
