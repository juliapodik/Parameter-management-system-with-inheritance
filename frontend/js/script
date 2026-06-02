let currentId = null;
let currentType = null;

function showMessage(text, isError = false) {
    const msg = document.getElementById('message');
    msg.textContent = text;
    msg.className = `message ${isError ? 'error' : 'success'} show`;
    setTimeout(() => msg.classList.remove('show'), 3000);
}

async function api(url, method, body) {
    const opts = { method, headers: { 'Content-Type': 'application/json' } };
    if (body) opts.body = JSON.stringify(body);
    const res = await fetch(url, opts);
    if (!res.ok) throw new Error(await res.text());
    return res.json();
}

async function load() {
    try {
        const groups = await api('/groups');
        const elements = await api('/elements');
        
        const groupsDiv = document.getElementById('groupsList');
        let html = '';
        
        for (let g of groups) {
            let active = (currentType === 'group' && currentId === g.id);
            html += `
                <div class="item ${active ? 'active' : ''}">
                    <span class="item-name" onclick="selectGroup(${g.id})"> ${escapeHtml(g.name)}</span>
                    <button class="delete-btn" onclick="deleteGroup(${g.id}, '${escapeHtml(g.name)}')">
                        <img src="../images/icon-delete.svg" width="14" height="14" style="filter: brightness(0) invert(1);">
                    </button>
                </div>
            `;
        }
        
        for (let e of elements) {
            let group = groups.find(g => g.id === e.group_id);
            let active = (currentType === 'element' && currentId === e.id);
            html += `
                <div class="item ${active ? 'active' : ''}">
                    <span class="item-name" onclick="selectElement(${e.id})"> ${escapeHtml(e.name)} (${group ? escapeHtml(group.name) : '?'})</span>
                    <button class="delete-btn" onclick="deleteElement(${e.id}, '${escapeHtml(e.name)}')">
                        <img src="../images/icon-delete.svg" width="14" height="14" style="filter: brightness(0) invert(1);">
                    </button>
                </div>
            `;
        }
        
        if (groups.length === 0 && elements.length === 0) {
            html = '<div style="color:#7a80a0; text-align:center; padding:20px;">Нет данных</div>';
        }
        
        groupsDiv.innerHTML = html;
        
        const groupSelect = document.getElementById('groupSelect');
        groupSelect.innerHTML = '<option value="">Выберите группу</option>';
        for (let g of groups) {
            groupSelect.innerHTML += `<option value="${g.id}">${escapeHtml(g.name)}</option>`;
        }
    } catch (e) {
        showMessage('Ошибка загрузки', true);
    }
}

async function deleteGroup(id, name) {
    if (!confirm(`Удалить группу "${name}" и все её элементы?`)) return;
    try {
        await api(`/groups/${id}`, 'DELETE');
        if (currentId === id) { currentId = null; currentType = null; document.getElementById('params').innerHTML = ''; }
        await load();
        showMessage(`Группа "${name}" удалена`);
    } catch (e) {
        showMessage('Ошибка удаления', true);
    }
}

async function deleteElement(id, name) {
    if (!confirm(`Удалить элемент "${name}"?`)) return;
    try {
        await api(`/elements/${id}`, 'DELETE');
        if (currentId === id) { currentId = null; currentType = null; document.getElementById('params').innerHTML = ''; }
        await load();
        showMessage(`Элемент "${name}" удалён`);
    } catch (e) {
        showMessage('Ошибка удаления', true);
    }
}

async function createGroup() {
    let name = document.getElementById('newGroup').value.trim();
    if (!name) { showMessage('Введите название', true); return; }
    try {
        await api('/groups', 'POST', { name });
        document.getElementById('newGroup').value = '';
        await load();
        showMessage(`Группа "${name}" создана`);
    } catch (e) {
        showMessage('Ошибка создания', true);
    }
}

async function createElementBtn() {
    let name = document.getElementById('newElement').value.trim();
    let groupId = document.getElementById('groupSelect').value;
    if (!name) { showMessage('Введите имя элемента', true); return; }
    if (!groupId) { showMessage('Выберите группу', true); return; }
    try {
        await api('/elements', 'POST', { name, group_id: parseInt(groupId) });
        document.getElementById('newElement').value = '';
        await load();
        showMessage(`Элемент "${name}" создан`);
    } catch (e) {
        showMessage('Ошибка создания', true);
    }
}

async function selectGroup(id) {
    currentId = id;
    currentType = 'group';
    document.getElementById('title').innerHTML = 'Редактирование группы';
    await load();
    let params = await api(`/groups/${id}/params`);
    renderParams(params, false);
}

async function selectElement(id) {
    currentId = id;
    currentType = 'element';
    document.getElementById('title').innerHTML = 'Редактирование элемента';
    await load();
    let data = await api(`/elements/${id}/resolved_params`);
    renderParams(data.resolved, true, data.overridden, data.inherited);
}

function renderParams(params, isElement, overridden = {}, inherited = {}) {
    let container = document.getElementById('params');
    let html = '<div id="paramList">';
    
    if (Object.keys(params).length === 0) {
        html += '<div style="color:#7a80a0; text-align:center; padding:20px;">Нет параметров</div>';
    } else {
        for (let [name, value] of Object.entries(params)) {
            let isOverridden = isElement && (name in overridden);
            let cls = '';
            let hint = '';
            
            if (isOverridden) {
                cls = 'overridden';
                hint = `Не ${inherited[name] || 'от группы'}`;
            } else if (isElement && (name in inherited)) {
                cls = 'inherited';
                hint = 'От группы';
            }
            
            html += `
                <div class="param-row ${cls}">
                    <strong>${escapeHtml(name)}:</strong>
                    <input type="text" id="val_${escapeHtml(name)}" value="${escapeHtml(value)}">
                    <span style="font-size:12px; color:#8a90a8;">${hint}</span>
                    <button onclick="this.closest('.param-row').remove()">
                        <img src="../images/icon-delete.svg" width="14" height="14" style="filter: brightness(0) invert(1);">
                    </button>
                </div>
            `;
        }
    }
    
    html += '</div>';
    html += '<hr style="margin: 16px 0; border-color:#2a2f3e;">';
    html += '<div style="display: flex; gap: 10px; flex-wrap: wrap;">';
    html += '<input type="text" id="newName" placeholder="Имя параметра" style="flex:2;">';
    html += '<input type="text" id="newValue" placeholder="Значение" style="flex:1;">';
    html += '<button class="add-btn" onclick="addParam()">+ Добавить</button>';
    html += '</div>';
    html += '<button class="success" onclick="saveParams()" style="margin-top: 16px;">СОХРАНИТЬ</button>';
    
    container.innerHTML = html;
}

function addParam() {
    let name = document.getElementById('newName').value.trim();
    let value = document.getElementById('newValue').value.trim();
    if (!name) { showMessage('Введите имя параметра', true); return; }
    
    let paramList = document.getElementById('paramList');
    let newRow = document.createElement('div');
    newRow.className = 'param-row';
    newRow.innerHTML = `
        <strong>${escapeHtml(name)}:</strong>
        <input type="text" id="val_${escapeHtml(name)}" value="${escapeHtml(value)}">
        <span style="font-size:12px; color:#8a90a8;"></span>
        <button onclick="this.closest('.param-row').remove()">
            <img src="../images/icon-delete.svg" width="14" height="14" style="filter: brightness(0) invert(1);">
        </button>
    `;
    paramList.appendChild(newRow);
    document.getElementById('newName').value = '';
    document.getElementById('newValue').value = '';
    showMessage(`Параметр "${name}" добавлен`);
}

async function saveParams() {
    let params = {};
    let inputs = document.querySelectorAll('#paramList input[id^="val_"]');
    for (let input of inputs) {
        let name = input.id.replace('val_', '');
        params[name] = input.value;
    }
    
    if (Object.keys(params).length === 0) {
        showMessage('Нет параметров для сохранения', true);
        return;
    }
    
    try {
        if (currentType === 'group') {
            await api(`/groups/${currentId}/params`, 'PUT', params);
            showMessage('Параметры сохранены!');
            await selectGroup(currentId);
        } else {
            let data = await api(`/elements/${currentId}/resolved_params`);
            let overridden = {};
            for (let [name, value] of Object.entries(params)) {
                if (data.resolved[name] !== value) {
                    overridden[name] = value;
                }
            }
            await api(`/elements/${currentId}/params`, 'PUT', overridden);
            showMessage('Переопределения сохранены!');
            await selectElement(currentId);
        }
    } catch (e) {
        showMessage('Ошибка сохранения', true);
    }
}

function escapeHtml(str) {
    if (!str) return '';
    return String(str).replace(/[&<>]/g, function(m) {
        if (m === '&') return '&amp;';
        if (m === '<') return '&lt;';
        if (m === '>') return '&gt;';
        return m;
    });
}

load();
