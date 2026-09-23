from datetime import datetime, timezone

def build_warning(location):
    if location.get('riskLevel') not in {'high','critical'} and location.get('trend') != 'increasing': return None
    return {'id':f"w-{location['id']}",'locationId':location['id'],'location':f"{location['name']}, {location['state']}",'riskLevel':location['riskLevel'],'rainfall':location.get('rainfall',0),'probability':round(float(location.get('probability',0))*100),'change':0,'timestamp':datetime.now(timezone.utc).isoformat(),'source':location.get('modelSource','backend')}
