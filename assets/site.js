/* XIAI JEWELRY — menu, jewellery dropdown, product gallery, filters, enquiry prefill */
(function () {
  var doc = document;

  // Mobile drawer
  var drawer = doc.getElementById('drawer');
  var openBtn = doc.querySelector('.menu-btn');
  if (drawer && openBtn) {
    var closeBtn = drawer.querySelector('.drawer-close');
    var setOpen = function (open) {
      drawer.classList.toggle('open', open);
      drawer.setAttribute('aria-hidden', open ? 'false' : 'true');
      openBtn.setAttribute('aria-expanded', open ? 'true' : 'false');
      doc.body.classList.toggle('locked', open);
      if (open) { setTimeout(function () { closeBtn.focus(); }, 80); } else { openBtn.focus(); }
    };
    openBtn.addEventListener('click', function () { setOpen(true); });
    closeBtn.addEventListener('click', function () { setOpen(false); });
    doc.addEventListener('keydown', function (e) {
      if (e.key === 'Escape' && drawer.classList.contains('open')) { setOpen(false); }
    });
  }

  // Jewellery dropdown (click/keyboard; hover handled in CSS)
  doc.querySelectorAll('.has-mega').forEach(function (item) {
    var btn = item.querySelector('button');
    btn.addEventListener('click', function () {
      var open = !item.classList.contains('open');
      item.classList.toggle('open', open);
      btn.setAttribute('aria-expanded', open ? 'true' : 'false');
    });
    item.addEventListener('keydown', function (e) {
      if (e.key === 'Escape') { item.classList.remove('open'); btn.setAttribute('aria-expanded', 'false'); btn.focus(); }
    });
    doc.addEventListener('click', function (e) {
      if (!item.contains(e.target)) { item.classList.remove('open'); btn.setAttribute('aria-expanded', 'false'); }
    });
  });

  // Product gallery
  var main = doc.getElementById('gal-main');
  if (main) {
    var thumbs = doc.querySelectorAll('.thumbs button');
    thumbs.forEach(function (b) {
      b.addEventListener('click', function () {
        main.src = b.dataset.src;
        main.alt = b.dataset.alt;
        thumbs.forEach(function (x) { x.removeAttribute('aria-current'); });
        b.setAttribute('aria-current', 'true');
      });
    });
  }

  // Pearl filters on listing pages
  var chips = doc.querySelectorAll('[data-filter]');
  if (chips.length) {
    var cards = doc.querySelectorAll('.grid .card');
    var shown = doc.getElementById('shown');
    var apply = function (key) {
      var n = 0;
      cards.forEach(function (c) {
        var ok = key === 'all' || (' ' + c.dataset.pearls + ' ').indexOf(' ' + key + ' ') > -1;
        c.hidden = !ok;
        if (ok) { n++; }
      });
      chips.forEach(function (x) { x.setAttribute('aria-pressed', x.dataset.filter === key ? 'true' : 'false'); });
      if (shown) { shown.textContent = n + (n === 1 ? ' piece' : ' pieces'); }
    };
    chips.forEach(function (c) { c.addEventListener('click', function () { apply(c.dataset.filter); }); });
  }

  // Enquiry prefill on the contact page: /contact?item=33168
  var asking = doc.getElementById('asking');
  if (asking) {
    var m = /[?&]item=(\d{5})\b/.exec(location.search);
    if (m) {
      var names = JSON.parse(asking.dataset.names || '{}');
      var label = names[m[1]] ? names[m[1]] + ' (No. ' + m[1] + ')' : 'item no. ' + m[1];
      asking.querySelector('b').textContent = label;
      asking.classList.add('show');
    }
  }
})();
