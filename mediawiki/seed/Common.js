(function () {
  function ready(fn) {
    if (document.readyState !== 'loading') {
      fn();
    } else {
      document.addEventListener('DOMContentLoaded', fn);
    }
  }

  ready(function () {
    var box = document.querySelector('.uu-controls');
    if (!box) {
      return;
    }

    var page = box.getAttribute('data-page');
    var fields = ['register', 'dialect', 'stance'];
    var allowed = {
      register: ['ngoko', 'madya', 'krama', 'mixed', 'undetermined'],
      dialect: ['mataraman', 'jawa-timuran', 'banyumasan', 'undetermined'],
      stance: ['peer', 'deferential', 'assertive', 'mixed', 'undetermined']
    };

    var ui = document.createElement('div');
    ui.className = 'uu-widget';
    ui.style.border = '1px solid #ccc';
    ui.style.padding = '0.8em';
    ui.style.marginTop = '0.8em';
    ui.innerHTML = '<p><strong>Correct labels</strong> — confirm, correct, or reject without editing wikitext.</p>';

    fields.forEach(function (field) {
      var current = box.getAttribute('data-' + field) || '';
      var row = document.createElement('div');
      row.style.marginBottom = '0.6em';

      var label = document.createElement('label');
      label.textContent = field + ' (now: ' + current + ') ';
      row.appendChild(label);

      var sel = document.createElement('select');
      sel.setAttribute('aria-label', field);
      allowed[field].forEach(function (v) {
        var o = document.createElement('option');
        o.value = v;
        o.textContent = v;
        if (v === current) {
          o.selected = true;
        }
        sel.appendChild(o);
      });
      row.appendChild(sel);

      function btn(text, action) {
        var b = document.createElement('button');
        b.type = 'button';
        b.textContent = text;
        b.style.marginLeft = '0.35em';
        b.addEventListener('click', function () {
          var to = action === 'corrected' ? sel.value : current;
          post(field, current, to, action);
        });
        return b;
      }

      row.appendChild(btn('Confirm', 'confirmed'));
      row.appendChild(btn('Correct', 'corrected'));
      row.appendChild(btn('Reject', 'rejected'));
      ui.appendChild(row);
    });

    var status = document.createElement('p');
    status.id = 'uu-status';
    ui.appendChild(status);
    box.appendChild(ui);

    function post(field, from, to, action) {
      status.textContent = 'Saving…';
      fetch('http://localhost:8000/correction', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          page: page,
          field: field,
          from: from,
          to: to,
          action: action,
          actor_role: 'author'
        })
      }).then(function (r) {
        return r.json().then(function (j) {
          return { ok: r.ok, j: j };
        });
      }).then(function (res) {
        if (res.ok && res.j.written) {
          status.textContent = 'Saved (revision ' + res.j.revision + '). Reloading…';
          setTimeout(function () {
            location.reload();
          }, 700);
        } else {
          status.textContent = 'Could not save: ' + JSON.stringify(res.j);
        }
      }).catch(function (e) {
        status.textContent = 'Could not save: ' + e;
      });
    }
  });
})();
