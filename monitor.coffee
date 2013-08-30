ws = new WebSocket('ws://localhost:12345')
#ws = new WebSocket('ws://80.56.96.111:12345')
ws.onopen = -> console.log 'open'
ws.onclose = -> console.log 'close'
ws.onerror = (e) -> console.log 'error', e
ws.onmessage = (msg) -> console.log 'msg', msg.data
#ws.onmessage = (msg) -> console.log 'msg', JSON.parse(msg.data)
