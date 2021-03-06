el = (id) -> document.getElementById(id)
set = (id, value) -> el(id).innerHTML = value
values = (e for e in el('content').getElementsByTagName('span')) \
         .concat(el('osname'))

connect = ->
    val.innerHTML = 'Connecting...' for val in values
    ws = new WebSocket 'ws://kompiler.org:8100'

    ws.onopen = ->
        console.log 'open'
        el('status').className = 'right online'
        set('status', '<i class="icon-off"></i>Online')

    ws.onclose = ->
        console.log 'close'
        val.innerHTML = '-' for val in values
        el('status').className = 'right offline'
        set('status', '<i class="icon-off"></i>Offline')
        setTimeout connect, 5000

    ws.onerror = (e) ->
        console.log 'error', e

    ws.onmessage = (msg) ->
        console.log 'msg', msg.data
        data = JSON.parse(msg.data)

        set('osname', data.osname) if data.osname
        set('uptime', fmt_time(data.uptime)) if data.uptime
        set('cpu-usage', "#{data.cpu_usage}%")
        set('memory', fmt_kbytes_usage(data.memory))
        set('disk', fmt_kbytes_usage(data.disk))

        if data.temps
            el('temp').innerHTML = ("#{deg}&#8451;" for deg in data.temps) \
                                   .join('&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;')
        else
            set('temp', '-')

fmt_time = (total) ->
    total = Math.round total
    s = (n) -> if n == 1 then '' else 's'

    secs = total % 60
    str = "#{secs} second" + s(secs)

    if total >= 60
        mins = parseInt total % (60 * 60) / 60
        str = "#{mins} minute#{s(mins)}, #{str}"

    if total >= 60 * 60
        hours = parseInt total % (60 * 60 * 24) / (60 * 60)
        str = "#{hours} hour#{s(hours)}, #{str}"

    str

fmt_kbytes_usage = ([used, total]) ->
    used = Math.round used / 1e6
    total = Math.round total / 1e6
    perc = Math.round used / total * 100
    return "#{used}MB / #{total}MB (#{perc}%)"

connect()
