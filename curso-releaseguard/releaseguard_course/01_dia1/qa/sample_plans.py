from qa.schemas import TestPlan

def insufficient_stock_plan() -> TestPlan:
    return TestPlan.model_validate({
      'name':'checkout bloqueia quantidade acima do estoque',
      'intent':'validar que carrinho rejeita quantidade maior que o estoque disponível',
      'risk':'overselling e inconsistência de estoque',
      'oracle':'a API de carrinho deve responder HTTP 409 para quantidade acima do estoque',
      'steps':[
        {'name':'criar carrinho','method':'POST','path':'/cart','expect_status':200},
        {'name':'adicionar quantidade inválida','method':'POST','path':'/cart/{cart_id}/items','json_body':{'product_id':'sku-001','quantity':99},'expect_status':409}
      ]})
