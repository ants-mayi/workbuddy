// 真实 DOM 端到端测试：加载整页 + marked v12，验证左侧二级目录与跳转
const { JSDOM } = require('jsdom');
const fs = require('fs');
const BASE = process.env.ENV_CONSOLE_PORT
  ? `http://127.0.0.1:${process.env.ENV_CONSOLE_PORT}`
  : 'http://127.0.0.1:8010';

(async () => {
  // 预取接口数据供 fetch stub 使用
  const meta = await fetch(BASE + '/api/meta').then(r => r.json());
  const docsData = await fetch(BASE + '/api/docs').then(r => r.json());
  const apiData = { '/api/meta': meta, '/api/docs': docsData };

  const dom = await JSDOM.fromFile('engine/index.html', {
    runScripts: 'dangerously',
    resources: 'usable',
    url: BASE + '/',
    beforeParse(window) {
      window.fetch = url => Promise.resolve({
        json: () => {
          const p = String(url).split('?')[0];
          if (apiData[p]) return Promise.resolve(apiData[p]);
          return fetch(BASE + p).then(r => r.json());
        }
      });
      window.HTMLElement.prototype.scrollIntoView = function () {
        window.__scrolls = window.__scrolls || [];
        window.__scrolls.push(this.id || this.tagName);
      };
      if (!window.CSS || !window.CSS.escape) {
        window.CSS = window.CSS || {};
        window.CSS.escape = s => String(s).replace(/[^a-zA-Z0-9_\-]/g, c => '\\' + c);
      }
    }
  });
  const { window } = dom;
  const { document } = window;
  const sleep = ms => new Promise(r => setTimeout(r, ms));
  let pass = 0, fail = 0;
  const ok = (cond, name) => { if (cond) { pass++; console.log('  ✓ ' + name); } else { fail++; console.log('  ✗ ' + name); } };

  // 等待 marked 加载 + init/buildNavToc 完成
  for (let i = 0; i < 30 && !(document.querySelectorAll('#nav-toc .nd-name').length > 0); i++) await sleep(200);
  console.log('== 左侧二级目录 ==');
  const names = [...document.querySelectorAll('#nav-toc .nd-name')];
  ok(names.length === 9, `生成 ${names.length} 个文档条目（预期 9）`);
  ok(document.querySelectorAll('#nav button[data-k="docs"]').length === 1, '「速查文档」主导航存在');

  console.log('== 点击左侧文档名 → 打开对应文档 ==');
  names[2].click();
  await sleep(100);
  ok(document.getElementById('p-docs').classList.contains('show'), '自动切到速查文档面板');
  const active = document.querySelector('#dtabs button.active');
  ok(active && active.dataset.i === '2', `激活文档 tab = ${active && active.dataset.i}（预期 2）`);
  ok(document.getElementById('dbody').innerHTML.length > 500, '正文已渲染');

  console.log('== 正文标题 id（跳转命中的前提）==');
  const hs = [...document.querySelectorAll('#dbody h1,#dbody h2,#dbody h3')];
  const noId = hs.filter(h => !h.id);
  ok(hs.length > 0 && noId.length === 0, `${hs.length} 个标题全部有 id（缺 ${noId.length}）`);

  console.log('== 点击左侧目录项 → 滚动到小节 ==');
  window.__scrolls = [];
  const items = [...document.querySelectorAll('#nav-toc a')];
  ok(items.length > 0, `展开的文档目录有 ${items.length} 项`);
  const target = items[Math.min(2, items.length - 1)];
  const anchor = target.dataset.anchor;
  target.click();
  await sleep(50);
  const el = document.querySelector(`#dbody [id="${window.CSS.escape(anchor)}"]`);
  ok(!!el, `锚点元素存在: #${anchor}`);
  ok(window.__scrolls.includes(anchor), 'scrollIntoView 被调用且目标正确');

  console.log('== 文档内锚点链接 ==');
  window.__scrolls = [];
  const mdAnchor = [...document.querySelectorAll('#dbody a[href^="#"]')][0];
  if (mdAnchor) {
    mdAnchor.click();
    await sleep(50);
    const key = decodeURIComponent(mdAnchor.getAttribute('href').slice(1));
    ok(window.__scrolls.length > 0 && window.__scrolls.includes(key), `文内锚点跳转生效: ${key}`);
  } else console.log('  （当前文档无文内锚点，跳过）');

  console.log('== 跨文档 .md 链接 ==');
  const mdLink = [...document.querySelectorAll('#dbody a')].find(a => /\.md($|#|\?)/i.test(a.getAttribute('href') || ''));
  if (mdLink) {
    const tgtName = decodeURIComponent(mdLink.getAttribute('href')).replace(/\.md($|\?|#).*$/i, '').split('/').pop();
    mdLink.click();
    await sleep(100);
    const act = document.querySelector('#dtabs button.active');
    ok(act && act.dataset.i !== '2', `切换到其它文档 tab=${act && act.dataset.i}`);
    // nav-toc 被 renderNavToc 重建过，必须重新查询
    const names2 = [...document.querySelectorAll('#nav-toc .nd-name')];
    const on = names2.find(n => n.classList.contains('on'));
    ok(on && on.dataset.i === act.dataset.i, `左侧目录展开状态同步: ${on && on.textContent} === ${tgtName}`);
    console.log('== 再次点击已展开文档名 → 收起 ==');
    names2[+act.dataset.i].click();
    await sleep(50);
    const names3 = [...document.querySelectorAll('#nav-toc .nd-name')];
    ok(!names3.some(n => n.classList.contains('on')), '目录收起');
  } else console.log('  （当前文档无跨文档链接，跳过）');

  console.log('== 收起/展开逻辑补测 ==');

  console.log(`\n结果: ${pass} 通过, ${fail} 失败`);
  process.exit(fail ? 1 : 0);
})().catch(e => { console.error('TEST ERROR:', e.message); process.exit(2); });
