from release.policy import decide

def test_healthy_release_passes():
    assert decide({'passed':True},{'policy':'pass','triage':{'recommendation':'accept'}},{'active_incident':False}).decision=='PASS'

def test_visual_block_blocks():
    assert decide({'passed':True},{'policy':'pass','triage':{'recommendation':'block'}},{'active_incident':False}).decision=='BLOCK'

def test_active_incident_blocks():
    assert decide({'passed':True},{'policy':'pass','triage':{'recommendation':'accept'}},{'active_incident':True}).decision=='BLOCK'
