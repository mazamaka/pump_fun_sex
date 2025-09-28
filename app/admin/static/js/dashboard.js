(function(){
  function init(){
    const statusEl = document.getElementById('ws-status');
    const totalEl = document.getElementById('total');
    const rowsEl = document.getElementById('rows');

    if (!statusEl || !totalEl || !rowsEl){
      console.warn('[WS] required elements not found');
      return;
    }

    console.info('[WS] dashboard.js loaded');

    let total = 0;
    let ws = null;
    let pingTimer = null;

    function addRow(evt) {
      total += 1;
      totalEl.textContent = String(total);
      const tr = document.createElement('tr');
      const t = new Date().toLocaleTimeString();
      tr.innerHTML = `
        <td>${t}</td>
        <td><span class="pill">${evt.symbol ?? ''}</span></td>
        <td>${evt.name ?? ''}</td>
        <td><code>${evt.signature ?? ''}</code></td>
        <td><code>${evt.mint ?? ''}</code></td>
        <td>${evt.marketCapSol ?? ''}</td>
        <td>${evt.solAmount ?? ''}</td>
        <td>${evt.initialBuy ?? ''}</td>
        <td>${evt.pool ?? ''}</td>
      `;
      rowsEl.prepend(tr);
      const limit = 200;
      while (rowsEl.children.length > limit) rowsEl.removeChild(rowsEl.lastChild);
    }

    function cleanup() {
      if (pingTimer) { clearInterval(pingTimer); pingTimer = null; }
      if (ws) { try { ws.close(); } catch (e) {} ws = null; }
    }

    function connect() {
      cleanup();
      statusEl.textContent = 'connecting';
      const proto = location.protocol === 'https:' ? 'wss' : 'ws';
      const url = `${proto}://${location.host}/ws/tokens`;
      console.info('[WS] connect', url);
      ws = new WebSocket(url);

      ws.onopen = () => {
        statusEl.textContent = 'connected';
        console.info('[WS] open');
        pingTimer = setInterval(() => { try { ws.send('ping'); } catch (e) {} }, 20000);
      };

      ws.onmessage = (ev) => {
        try {
          const data = JSON.parse(ev.data);
          if (data && data.type === 'new_token') addRow(data);
        } catch (_) {}
      };

      ws.onclose = () => {
        statusEl.textContent = 'reconnecting';
        console.warn('[WS] close - reconnect in 1000ms');
        cleanup();
        setTimeout(connect, 1000);
      };

      ws.onerror = () => {
        statusEl.textContent = 'error';
        console.error('[WS] error');
        cleanup();
      };
    }

    connect();
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
})();
