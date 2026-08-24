from types import SimpleNamespace

from supportops.agent import _resume_after_human_review


class FakeGraph:
    def __init__(self):
        self.commands = []

    def invoke(self, command, config):
        self.commands.append((command, config))
        return {"messages": []}


def _interrupted_result():
    return {
        "__interrupt__": [
            SimpleNamespace(
                value={
                    "action_requests": [
                        {
                            "name": "invalidate_permission_cache",
                            "arguments": {"user_id": "usr-104"},
                        }
                    ]
                }
            )
        ]
    }


def test_human_can_approve_protected_tool():
    graph = FakeGraph()
    config = {"configurable": {"thread_id": "test"}}

    result = _resume_after_human_review(
        graph,
        _interrupted_result(),
        config,
        approval_handler=lambda action: True,
    )

    assert result == {"messages": []}
    command, received_config = graph.commands[0]
    assert command.resume == {"decisions": [{"type": "approve"}]}
    assert received_config == config


def test_human_can_reject_protected_tool():
    graph = FakeGraph()

    _resume_after_human_review(
        graph,
        _interrupted_result(),
        {"configurable": {"thread_id": "test"}},
        approval_handler=lambda action: False,
    )

    command, _ = graph.commands[0]
    decision = command.resume["decisions"][0]
    assert decision["type"] == "reject"
    assert "Não tente executar novamente" in decision["message"]
