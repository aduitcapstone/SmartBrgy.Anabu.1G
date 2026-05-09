/**
 * SmartBrgy DB Connector v2 — KUMPLETO
 * I-include pagkatapos ng script.js sa index.html:
 *   <script src="script.js"></script>
 *   <script src="db-connector.js"></script>
 *
 * Lahat ng save/submit/update → naka-save na sa SQLite database
 */

var _DB_API = (window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1' || window.location.hostname === '')
  ? 'http://localhost:5000'
  : 'https://smartbrgy-anabu-1g.onrender.com';

// ── HTTP helpers ──────────────────────────────────────────────
const http = {
  async get(path) {
    try { const r = await fetch(_DB_API+path); return r.ok ? r.json() : null; }
    catch(e) { console.warn('GET',path,e.message); return null; }
  },
  async post(path, body) {
    try { const r = await fetch(_DB_API+path,{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(body)}); return r.json(); }
    catch(e) { console.warn('POST',path,e.message); return null; }
  },
  async put(path, body) {
    try { const r = await fetch(_DB_API+path,{method:'PUT',headers:{'Content-Type':'application/json'},body:JSON.stringify(body)}); return r.json(); }
    catch(e) { console.warn('PUT',path,e.message); return null; }
  },
  async del(path) {
    try { const r = await fetch(_DB_API+path,{method:'DELETE'}); return r.json(); }
    catch(e) { console.warn('DELETE',path,e.message); return null; }
  },
};

// ── Format converters ─────────────────────────────────────────
function dbToResident(r) {
  let specialGroups = [];
  try { specialGroups = JSON.parse(r.special_groups || '[]'); } catch(e) {}
  return { id:r.id, name:r.name, purok:r.purok||'', dob:r.dob||'', gender:r.gender||'',
    civil:r.civil||'', contact:r.contact||'', status:r.status||'Active',
    household:r.household||'', type:r.type||'', address:r.address||'',
    specialGroups,
    _goodStanding: r.good_standing !== undefined ? !!r.good_standing : true,
    _blotter: !!r.blotter, _blotterDetails: r.blotter_details || [] };
}
function dbToCertReq(r) {
  return { code:r.code, name:r.name, type:r.type, requested:r.requested,
    status:r.status, via:r.via, cert_id:r.cert_id, purpose:r.purpose,
    address:r.address, contact:r.contact, email:r.email||'', attachment:r.attachment||'',
    dob:r.dob||'', resident_id:r.resident_id, source:r.source, hidden: !!r.hidden };
}

window.hideCertRequest = async function(code) {
  if (!confirm(`Alisin ang ${code} sa listahan? Mananatili pa rin ito sa Done count.`)) return;
  const result = await http.put(`/api/cert-requests/${code}/hide`, {});
  if (result) {
    const req = CERT_REQUESTS.find(r => r.code === code);
    if (req) req.hidden = true;
    if (typeof renderCertKanban === 'function') renderCertKanban();
    addLiveAuditEntry('🗑️', 'cert', 'Certificate Request Removed', `${code} — Naalis sa kanban board`, 'Staff');
    showToast(`🗑️ ${code} naalis sa listahan.`, 'green');
  }
};
function dbToIncident(r) {
  let atts = r.attachments;
  if (Array.isArray(atts)) {
    // already correct
  } else if (typeof atts === 'string' && atts) {
    try {
      atts = JSON.parse(atts);
      if (!Array.isArray(atts)) {
        try { atts = JSON.parse(atts); } catch(e) { atts = []; }
        if (!Array.isArray(atts)) atts = [];
      }
    } catch(e) { atts = []; }
  } else {
    atts = [];
  }
  return { id:r.id, type:r.type, loc:r.location, date:r.date,
    reported:r.reported_by, complainee:r.complainee||'', description:r.description||'',
    status:r.status, severity:r.severity, attachments: atts };
}
function dbToUser(r) {
  return { id:r.id, name:r.name, role:r.role, access:r.access,
    username:r.username, face:!!r.face, rfid:!!r.rfid,
    status:r.status, last:r.last_login||'—' };
}
function rebuildStatus(residents) {
  const s = {};
  residents.forEach(r => { s[r.id] = { blotter:r._blotter||false, blotterDetails:r._blotterDetails||[], goodStanding:r._goodStanding!==undefined?r._goodStanding:true, notes:'' }; });
  return s;
}

// ── Refresh helpers ───────────────────────────────────────────
async function reloadResidents() {
  const data = await http.get('/api/residents');
  if (!data) return;
  const mapped = data.map(dbToResident);
  RESIDENTS.length = 0; mapped.forEach(r => RESIDENTS.push(r));
  const ns = rebuildStatus(mapped);
  Object.keys(ns).forEach(k => { RESIDENT_STATUS[k] = ns[k]; });
  // ── Recompute purok totals from live data ──
  PUROK_DATA.forEach(p => {
    p.total = RESIDENTS.filter(r => r.purok === p.key && r.status === 'Active').length;
  });
  const totalActive = RESIDENTS.filter(r => r.status === 'Active').length;
  PUROK_DATA.forEach(p => {
    p.pct = totalActive > 0 ? Math.round((p.total / totalActive) * 100) : 0;
  });
  if (typeof renderResidentsTable === 'function') renderResidentsTable();
  if (typeof populateEligResidentDropdown === 'function') populateEligResidentDropdown();
  if (typeof renderDemographics === 'function') renderDemographics();
  if (typeof renderDashPurokBreakdown === 'function') renderDashPurokBreakdown();
  if (typeof refreshPopulationStats === 'function') refreshPopulationStats();
}

// ── Dashboard stats realtime refresh ──────────────────────────
async function refreshDashboardStats() {
  const stats = await http.get('/api/dashboard/stats');
  const set = (id, val) => { const el = document.getElementById(id); if (el) el.textContent = val; };

  if (stats) {
    // Total residents counter
    document.querySelectorAll('.counter[data-target]').forEach(el => {
      const label = el.closest('.stat-card')?.querySelector('.stat-label')?.textContent || '';
      if (label.includes('Population') || label.includes('Resident')) {
        el.dataset.target = stats.total_residents;
        el.textContent = stats.total_residents.toLocaleString();
      }
    });
    // Pending requests = all non-completed
    const pending = (stats.total_requests || 0) - (stats.completed_requests || 0);
    set('dash-stat-pending',  pending);
    set('dash-sub-pending',   pending > 0 ? `${pending} request na hindi pa tapos` : 'No pending requests');
    // Incident reports = total
    const incTotal = stats.total_incidents !== undefined ? stats.total_incidents : stats.pending_incidents;
    set('dash-stat-incidents', incTotal);
    set('dash-sub-incidents',  incTotal > 0 ? `${incTotal} incident${incTotal !== 1 ? 's' : ''} na naka-file` : 'No incidents filed');
  } else {
    // Fallback: compute from in-memory arrays
    const reqs = typeof CERT_REQUESTS !== 'undefined' ? CERT_REQUESTS : [];
    const incs = typeof INCIDENTS !== 'undefined' ? INCIDENTS : [];
    const pending = reqs.filter(r => r.status !== 'Completed').length;
    set('dash-stat-pending',   pending);
    set('dash-sub-pending',    pending > 0 ? `${pending} request na hindi pa tapos` : 'No pending requests');
    set('dash-stat-incidents', incs.length);
    set('dash-sub-incidents',  incs.length > 0 ? `${incs.length} incident${incs.length !== 1 ? 's' : ''} na naka-file` : 'No incidents filed');
  }

  // Recent Activity from audit logs
  const logs = typeof LIVE_AUDIT_LOGS !== 'undefined' ? LIVE_AUDIT_LOGS : [];
  const actEl = document.getElementById('dash-recent-activity');
  if (actEl) {
    const typeColor = { auth:'var(--green-500)', cert:'#F59E0B', rfid:'var(--blue-400)', record:'#A78BFA', incident:'#FB923C', security:'#EF4444' };
    const recent = logs.slice(0, 6);
    if (recent.length === 0) {
      actEl.innerHTML = '<div style="text-align:center;color:var(--text-muted);font-size:11px;padding:18px 0;">No recent activity.</div>';
    } else {
      actEl.innerHTML = recent.map(l => `
        <div style="display:flex;align-items:flex-start;gap:10px;padding:8px 0;border-bottom:1px solid var(--border);">
          <span style="font-size:16px;flex-shrink:0;">${l.icon || '📌'}</span>
          <div style="flex:1;min-width:0;">
            <div style="font-size:12px;font-weight:600;color:${typeColor[l.type]||'var(--text-primary)'};">${l.action}</div>
            <div style="font-size:11px;color:var(--text-muted);white-space:nowrap;overflow:hidden;text-overflow:ellipsis;">${l.detail}</div>
          </div>
          <div style="font-size:10px;color:var(--text-muted);flex-shrink:0;">${l.time}</div>
        </div>`).join('');
    }
  }
}
async function reloadCertRequests() {
  const data = await http.get('/api/cert-requests');
  if (!data) return;
  CERT_REQUESTS.length = 0; data.map(dbToCertReq).forEach(r => CERT_REQUESTS.push(r));
  if (typeof renderCertKanban === 'function') renderCertKanban();
  if (typeof renderCertRequests === 'function') renderCertRequests();
  if (typeof renderRequestRecords === 'function') renderRequestRecords();
  if (typeof refreshDashboardStats === 'function') refreshDashboardStats();
  if (typeof buildCharts === 'function') buildCharts();
}
async function reloadIncidents() {
  const data = await http.get('/api/incidents');
  if (!data) return;
  INCIDENTS.length = 0; data.map(dbToIncident).forEach(i => INCIDENTS.push(i));
  if (typeof renderIncidents === 'function') renderIncidents();
  if (typeof renderRequestRecords === 'function') renderRequestRecords();
  if (typeof refreshDashboardStats === 'function') refreshDashboardStats();
}
async function reloadUsers() {
  const data = await http.get('/api/users');
  if (!data) return;
  USERS.length = 0; data.map(dbToUser).forEach(u => USERS.push(u));
  if (typeof renderUsers === 'function') renderUsers();
}
async function reloadRFID() {
  const data = await http.get('/api/rfid');
  if (!data) return;
  RFID_TAGS.length = 0;
  data.forEach(t => RFID_TAGS.push({ id:t.id, name:t.name, loc:t.location, type:t.type, status:t.status }));
  if (typeof renderRFIDTags === 'function') renderRFIDTags();
}
async function reloadCabinetFolders() {
  const data = await http.get('/api/cabinet/folders');
  if (!data) return;
  CABINET_FOLDERS.length = 0;
  data.forEach(f => CABINET_FOLDERS.push({ id:f.id, name:f.name, rfid:f.rfid, drawer:f.drawer, status:f.status }));
  if (typeof renderCabinetFolders === 'function') renderCabinetFolders();
}

// ══════════════════════════════════════════════════════════════
// LOAD ALL DATA FROM DB ON LOGIN
// ══════════════════════════════════════════════════════════════
async function loadAllFromDB() {
  console.log('🔄 SmartBrgy: Naglo-load ng data mula sa database...');
  const [residents, certReqs, incidents, rfidTags, users, cabinetFolders, purokData, auditData] = await Promise.all([
    http.get('/api/residents'), http.get('/api/cert-requests'), http.get('/api/incidents'),
    http.get('/api/rfid'), http.get('/api/users'), http.get('/api/cabinet/folders'),
    http.get('/api/purok'), http.get('/api/audit?limit=50'),
  ]);

  let loaded = 0;

  // Always clear arrays first — DB is the single source of truth
  RESIDENTS.length = 0;
  CERT_REQUESTS.length = 0;
  INCIDENTS.length = 0;
  RFID_TAGS.length = 0;
  CABINET_FOLDERS.length = 0;
  PUROK_DATA.length = 0;

  if (residents?.length) {
    const m = residents.map(dbToResident);
    m.forEach(r => RESIDENTS.push(r));
    const ns = rebuildStatus(m);
    Object.keys(ns).forEach(k => { RESIDENT_STATUS[k] = ns[k]; });
    loaded++;
  }
  if (certReqs?.length) {
    certReqs.map(dbToCertReq).forEach(r => CERT_REQUESTS.push(r)); loaded++;
  }
  if (incidents?.length) {
    incidents.map(dbToIncident).forEach(i => INCIDENTS.push(i)); loaded++;
  }
  if (rfidTags?.length) {
    rfidTags.forEach(t => RFID_TAGS.push({ id:t.id, name:t.name, loc:t.location, type:t.type, status:t.status }));
    loaded++;
  }
  if (users?.length) {
    USERS.length = 0; users.map(dbToUser).forEach(u => USERS.push(u)); loaded++;
  }
  if (cabinetFolders?.length) {
    cabinetFolders.forEach(f => CABINET_FOLDERS.push({ id:f.id, name:f.name, rfid:f.rfid, drawer:f.drawer, status:f.status }));
    loaded++;
  }
  if (purokData?.length) {
    purokData.forEach(p => PUROK_DATA.push({ key:p.key_name, label:p.label, total:p.total, color:p.color, pct:p.pct }));
    if (typeof syncPurokSelects === 'function') syncPurokSelects();
    loaded++;
  }
  if (auditData?.length) {
    const dbLogs = auditData.map(a => ({
      icon:a.icon||'📌', type:a.category||'general', action:a.action,
      detail:a.detail||'', user:a.user||'System',
      time: a.created_at ? new Date(a.created_at).toLocaleString('en-PH') : '', severity:'ok'
    }));
    dbLogs.forEach(e => {
      if (!LIVE_AUDIT_LOGS.find(l => l.action===e.action && l.detail===e.detail))
        LIVE_AUDIT_LOGS.push(e);
    });
    loaded++;
  }

  // Re-render everything
  ['renderResidentsTable','renderCertKanban','renderIncidents','renderRFIDTags',
   'renderUsers','renderCabinetFolders','renderAuditLog','renderDashPurokBreakdown',
   'populateEligResidentDropdown','updateNotifBadge','refreshDashboardStats','buildCharts',
   'renderRequestRecords'].forEach(fn => {
    if (typeof window[fn] === 'function') window[fn]();
  });

  // Update dashboard stats — call twice: immediately and after a tick to ensure DOM is ready
  if (typeof refreshDashboardStats === 'function') refreshDashboardStats();
  setTimeout(() => { if (typeof refreshDashboardStats === 'function') refreshDashboardStats(); }, 300);

  if (loaded > 0) {
    console.log(`✅ SmartBrgy: ${loaded} modules loaded`);
    showToast('✅ Live data loaded mula sa database!', 'green');
  } else {
    console.warn('⚠️ Backend offline — demo data lang ang ginagamit.');
  }

  // Restore last active screen after data is loaded
  const savedScreen = localStorage.getItem('smartbrgy_active_screen');
  if (savedScreen && savedScreen !== 'dashboard' && typeof showScreen === 'function') {
    const navEl = document.querySelector(`.nav-item[onclick*="'${savedScreen}'"]`);
    showScreen(savedScreen, navEl || null);
  }
}

// ══════════════════════════════════════════════════════════════
// INTERCEPT: saveResident() — RESIDENTS FORM
// ══════════════════════════════════════════════════════════════
window.saveResident = async function() {
  const f = id => document.getElementById(id)?.value?.trim();
  const firstName = f('res-name');
  const lastName  = f('res-lastname');
  if (!firstName) { showToast('❌ Pakiusap ilagay ang pangalan.', 'red'); return; }
  const fullName = (firstName + (lastName ? ' ' + lastName : '')).trim();

  // Collect special groups
  const specialGroups = [...document.querySelectorAll('.res-special-group:checked')].map(el => el.value);

  const payload = {
    name: fullName,
    purok:    f('res-purok'),
    dob:      f('res-dob'),
    gender:   f('res-gender'),
    civil:    f('res-civil'),
    contact:  f('res-contact'),
    address:  f('res-address') || '',
    status:   f('res-status') || 'Active',
    household:f('res-household') || '',
    type:     f('res-type'),
    specialGroups,
    by: 'Staff'
  };

  const editId = document.getElementById('res-edit-id')?.value
              || document.getElementById('res-editing-id')?.value;
  let result;
  if (editId) {
    result = await http.put(`/api/residents/${editId}`, payload);
    if (result) showToast(`✅ Na-update ang record ni ${fullName}!`, 'green');
  } else {
    result = await http.post('/api/residents', payload);
    if (result?.id) showToast(`✅ Nai-add si ${fullName} (${result.id})!`, 'green');
  }

  if (!result) { showToast('❌ Hindi ma-save. Subukan ulit.', 'red'); return; }
  closeModal('modal-resident');
  await reloadResidents();
  // ── Realtime refresh ng dashboard at demographics ──
  if (typeof refreshDashboardStats === 'function') refreshDashboardStats();
  if (typeof renderDemographics === 'function')    renderDemographics();
  if (typeof renderDashPurokBreakdown === 'function') renderDashPurokBreakdown();
  if (typeof refreshPopulationStats === 'function') refreshPopulationStats();
};

// ══════════════════════════════════════════════════════════════
// INTERCEPT: submitPortalRequest() — PORTAL FORM
// ══════════════════════════════════════════════════════════════
window.submitPortalRequest = async function() {
  const f = id => document.getElementById(id)?.value?.trim();
  const name = f('portal-name'), addr = f('portal-address'), purpose = f('portal-purpose');
  if (!name||!addr||!purpose) { alert('Kumpletuhin ang lahat ng required fields.'); return; }

  // Upload attachment if provided
  let attachmentUrl = '';
  const fileInput = document.getElementById('portal-attachment');
  if (fileInput?.files?.length) {
    const fd = new FormData();
    fd.append('file', fileInput.files[0]);
    try {
      const up = await fetch('/api/upload', { method:'POST', body:fd });
      const upData = await up.json();
      if (upData.url) attachmentUrl = upData.url;
    } catch(e) { console.warn('[Upload]', e); }
  }

  const ct = CERTIFICATE_TYPES.find(c => c.id === selectedCertType);
  const result = await http.post('/api/cert-requests', {
    name, type:ct?.label||'Certificate', cert_id:selectedCertType,
    purpose, address:addr, contact:f('portal-contact')||'',
    email: f('portal-email')||'', via:'Online', source:'portal',
    attachment: attachmentUrl
  });
  if (result?.code) {
    document.getElementById('portal-confirm-code').textContent = result.code;
    document.getElementById('portal-form').style.display = 'none';
    document.getElementById('portal-confirm').classList.add('show');
    await reloadCertRequests();
    showToast(`📨 Request ${result.code} na-submit!`, 'green');
  } else {
    alert('May error sa pag-submit. Subukan ulit.');
  }
};

// ══════════════════════════════════════════════════════════════
// INTERCEPT: saveIncident() — INCIDENT FORM
// ══════════════════════════════════════════════════════════════
window.saveIncident = async function() {
  const f = id => document.getElementById(id)?.value?.trim();
  const type = f('inc-type');
  if (!type) { showToast('❌ Piliin ang uri ng incident.', 'red'); return; }
  const editId = f('inc-edit-id');

  // Upload attachments if provided
  const attachmentUrls = [];
  const fileInput = document.getElementById('inc-attachments');
  if (fileInput?.files?.length) {
    for (const file of fileInput.files) {
      const fd = new FormData();
      fd.append('file', file);
      try {
        const up = await fetch('/api/upload', { method:'POST', body:fd });
        const upData = await up.json();
        if (upData.url) attachmentUrls.push(upData.url);
      } catch(e) { console.warn('[Upload]', e); }
    }
  }

  const payload = {
    type,
    date:        f('inc-date')        || '',
    location:    f('inc-location')    || '',
    reported_by: f('inc-reported')    || 'Anonymous',
    complainee:  f('inc-complainee')  || '',
    severity:    f('inc-severity')    || 'Medium',
    description: f('inc-details')     || '',
    attachments: attachmentUrls,
  };
  let result;
  if (editId) {
    result = await http.put(`/api/incidents/${editId}`, payload);
    if (result && !result.error) {
      addLiveAuditEntry('✏️','incident','Incident Report Updated', editId, 'Staff');
      showToast(`✅ Incident ${editId} na-update!`, 'green');
      closeModal('modal-incident');
      await reloadIncidents();
    } else {
      showToast(`❌ ${result?.error || 'Hindi ma-update.'}`, 'red');
    }
  } else {
    result = await http.post('/api/incidents', payload);
    if (result?.id) {
      addLiveAuditEntry('🚨','incident','Incident Report Filed',`${result.id} — ${type}`,'Staff');
      showToast(`🚨 Incident ${result.id} na-file!`, 'green');
      closeModal('modal-incident');
      await reloadIncidents();
    } else {
      showToast('❌ Hindi ma-save. Subukan ulit.', 'red');
    }
  }
};

// ══════════════════════════════════════════════════════════════
// INTERCEPT: printCert() — UPDATE STATUS → Completed
// ══════════════════════════════════════════════════════════════
window.printCert = async function(code) {
  const result = await http.put(`/api/cert-requests/${code}/status`, { status:'Completed', user:'Staff' });
  if (result) {
    showToast(`🖨️ Certificate ${code} na-print — Completed!`, 'green');
    addLiveAuditEntry('🖨️','cert','Certificate Printed',code,'Staff');
    const req = CERT_REQUESTS.find(r => r.code===code);
    if (req) req.status = 'Completed';
    if (typeof renderCertKanban==='function') renderCertKanban();
    if (typeof renderCertRequests==='function') renderCertRequests();
  } else {
    showToast('❌ Hindi ma-update ang status.','red');
  }
};

// ══════════════════════════════════════════════════════════════
// INTERCEPT: runEligibilityCheck() — GAMIT ANG DB API
// ══════════════════════════════════════════════════════════════
window.runEligibilityCheck = async function() {
  const residentId = document.getElementById('elig-resident-select')?.value;
  const certId = document.getElementById('elig-doc-select')?.value;
  if (!residentId||!certId) { showToast('Piliin ang residente at dokumento.','red'); return; }
  const result = await http.post('/api/eligibility', { resident_id:residentId, cert_id:certId });
  if (!result) return;
  const el = document.getElementById('elig-result');
  const btn = document.getElementById('elig-proceed-btn');
  const color = result.eligible ? 'var(--green-500)' : '#EF4444';
  const bg = result.eligible ? 'var(--green-dim)' : 'rgba(239,68,68,0.06)';
  const border = result.eligible ? 'var(--border-green)' : 'rgba(239,68,68,0.3)';
  const headline = result.eligible ? '✅ ELIGIBLE — Maaaring i-issue ang dokumento' : '🚫 NOT ELIGIBLE — Hindi maaaring i-issue';
  const res = result.resident || RESIDENTS.find(r => r.id===residentId);
  el.style.display = 'block';
  el.innerHTML = `<div style="background:${bg};border:1px solid ${border};border-radius:var(--radius);padding:14px;margin-bottom:12px;">
    <div style="font-weight:700;color:${color};font-size:13px;margin-bottom:8px;">${headline}</div>
    <div style="font-size:12.5px;color:var(--text-secondary);margin-bottom:4px;"><strong style="color:var(--text-primary);">Residente:</strong> ${res?.name||residentId} — ${res?.dob?calcAge(res.dob)+' taong gulang':''}</div>
    <div style="font-size:12.5px;color:var(--text-secondary);margin-bottom:10px;"><strong style="color:var(--text-primary);">Dokumento:</strong> ${result.rule?.label||certId}</div>
    <div style="display:flex;flex-direction:column;gap:6px;">${result.reasons.map(r=>`<div style="font-size:12px;color:var(--text-secondary);line-height:1.5;">${r}</div>`).join('')}</div>
  </div>`;
  btn.style.display = result.eligible ? 'block' : 'none';
  window.currentEligResidentId = residentId;
  addLiveAuditEntry('🔍','cert','Eligibility Check',`${res?.name||residentId} — ${result.rule?.label||certId} — ${result.eligible?'ELIGIBLE':'NOT ELIGIBLE'}`,'Staff');
};

// ══════════════════════════════════════════════════════════════
// INTERCEPT: elig_proceedRequest() — SAVE REQUEST SA DB
// ══════════════════════════════════════════════════════════════
window.elig_proceedRequest = async function() {
  const residentId = document.getElementById('elig-resident-select')?.value;
  const certId = document.getElementById('elig-doc-select')?.value;
  const ct = CERTIFICATE_TYPES.find(c => c.id===certId);
  const resident = RESIDENTS.find(r => r.id===residentId);
  const result = await http.post('/api/cert-requests', {
    resident_id:residentId, name:resident?.name||'', type:ct?.label||'',
    cert_id:certId, purpose:'Issued via Eligibility Check',
    address:resident?.purok||'', contact:resident?.contact||'', via:'Walk-in', source:'staff'
  });
  if (result?.code) {
    CERT_REQUESTS.unshift({ code:result.code, name:resident?.name||'', type:ct?.label||'',
      requested:new Date().toLocaleString('en-PH'), status:'Processing', via:'Walk-in' });
    if (typeof renderCertKanban==='function') renderCertKanban();
    showToast(`✅ Request ${result.code} na-add!`, 'green');
    addLiveAuditEntry('📨','cert','Certificate Request Created',`${result.code} — ${resident?.name} — ${ct?.label}`,'Staff');
    closeModal('modal-eligibility-check');
  } else {
    showToast('❌ Hindi ma-save. Subukan ulit.', 'red');
  }
};

// ══════════════════════════════════════════════════════════════
// INTERCEPT: saveNewUser() — ADD + EDIT USER SA DB
// ══════════════════════════════════════════════════════════════
window.saveNewUser = async function() {
  const f      = id => document.getElementById(id)?.value?.trim();
  const name   = f('adduser-name');
  const pass   = document.getElementById('adduser-password')?.value || '';
  const role   = f('adduser-role') || 'Barangay Clerk';
  const access = f('adduser-access') || 'View Only';
  const username = f('adduser-username') || (name ? name.toLowerCase().replace(/\s+/g,'.') : '');
  const faceOn = document.getElementById('adduser-facetoggle')?.classList.contains('on');
  const editId = f('adduser-edit-id');

  if (!name) { showToast('❌ Pakiusap ilagay ang pangalan.','red'); return; }

  if (editId) {
    // ── EDIT MODE ──
    if (pass.length > 0 && pass.length < 8) { showToast('❌ Password ay dapat 8 characters man lang.','red'); return; }
    const u = USERS.find(x => x.id === editId);
    if (u) { u.name = name; u.role = role; u.access = access; u.username = username; u.face = faceOn; }
    const payload = { name, role, access, username, face: faceOn, rfid: u?.rfid||false, status: u?.status||'Active' };
    if (pass.length >= 8) payload.password = pass;
    const result = await http.put(`/api/users/${editId}`, payload);
    if (result) {
      if (pass.length >= 8 && typeof VALID_CREDENTIALS !== 'undefined') {
        const cred = VALID_CREDENTIALS.find(c => c.empId === editId || c.username === username);
        if (cred) { cred.password = pass; cred.username = username; cred.name = name; cred.role = role; }
      }
      closeModal('modal-adduser');
      await reloadUsers();
      addLiveAuditEntry('✏️','auth','User Updated',`${name} — ${role} — ${editId}`,'Admin');
      showToast(`✅ Na-update ang user na "${name}"!`,'green');
    } else {
      showToast('❌ Hindi ma-update. Subukan ulit.','red');
    }
  } else {
    // ── ADD MODE ──
    if (pass.length < 8) { showToast('❌ Ang password ay dapat 8 characters man lang.','red'); return; }
    const result = await http.post('/api/users', { name, role, access, username, password: pass, face: faceOn, rfid: false });
    if (result?.id) {
      if (typeof VALID_CREDENTIALS !== 'undefined') {
        const idx = VALID_CREDENTIALS.findIndex(c => c.username === username);
        if (idx > -1) VALID_CREDENTIALS.splice(idx, 1);
        VALID_CREDENTIALS.push({ empId: result.id, username, password: pass, name, role });
      }
      closeModal('modal-adduser');
      await reloadUsers();
      addLiveAuditEntry('👤','auth','New User Created',`${name} — ${role} — ${result.id}`,'Admin');
      showToast(`✅ User "${name}" (${result.id}) na-create! Maaari na siyang mag-login.`,'green');
    } else {
      showToast('❌ Hindi ma-create ang user. Subukan ulit.','red');
    }
  }
};

// ══════════════════════════════════════════════════════════════
// INTERCEPT: suspendUser() at activateUser() — DB UPDATE
// ══════════════════════════════════════════════════════════════
window.suspendUser = async function(id) {
  const result = await http.put(`/api/users/${id}/suspend`, {});
  if (result) { await reloadUsers(); showToast('User suspended.',''); }
};
window.activateUser = async function(id) {
  const result = await http.put(`/api/users/${id}/activate`, {});
  if (result) { await reloadUsers(); showToast('User activated!','green'); }
};

// ══════════════════════════════════════════════════════════════
// INTERCEPT: Cabinet folders toggle — SAVE SA DB
// ══════════════════════════════════════════════════════════════
window.renderCabinetFolders = function() {
  const container = document.getElementById('cabinet-folders-list');
  if (!container) return;
  container.innerHTML = '';
  CABINET_FOLDERS.forEach(f => {
    const div = document.createElement('div');
    div.className = 'folder-item';
    div.innerHTML = `
      <span style="font-size:16px;">${f.status==='Checked Out'?'📂':'📁'}</span>
      <div style="flex:1;">
        <div style="font-weight:600;color:var(--text-primary);font-size:12px;">${f.name}</div>
        <div style="font-size:10.5px;color:var(--text-muted);">${f.drawer}</div>
      </div>
      <span class="badge ${f.status==='In Cabinet'?'badge-green':'badge-amber'}" style="font-size:9.5px;">${f.status}</span>
      <span class="folder-rfid-badge">${f.rfid}</span>`;
    div.onclick = async () => {
      const newStatus = f.status==='In Cabinet'?'Checked Out':'In Cabinet';
      const result = await http.put(`/api/cabinet/folders/${f.id}/status`, { status:newStatus, user:'Staff' });
      if (result) {
        f.status = newStatus;
        addLiveAuditEntry('📁','rfid',`Folder ${newStatus}`,`${f.id} — ${f.name}`,'Staff');
        showToast(`📁 ${f.name} — ${newStatus}. RFID ${f.rfid} na-log.`,'green');
        window.renderCabinetFolders();
      }
    };
    container.appendChild(div);
  });
};

// ══════════════════════════════════════════════════════════════
// INTERCEPT: Cabinet drawer log — SAVE SA DB
// ══════════════════════════════════════════════════════════════
const _origAddCabLog = window.addCabinetLog;
window.addCabinetLog = function(d, action) {
  if (typeof _origAddCabLog==='function') _origAddCabLog(d, action);
  http.post('/api/cabinet/log', { drawer_id:d.id, drawer_label:d.label, action, user:'Staff' }).catch(()=>{});
};

// ══════════════════════════════════════════════════════════════
// INTERCEPT: RFID scan — SAVE SA DB
// ══════════════════════════════════════════════════════════════
const _origSimRFID = window.simulateRFIDTag;
window.simulateRFIDTag = async function(tag) {
  const newStatus = tag.status==='In Cabinet'?'Checked Out':'In Cabinet';
  await http.post(`/api/rfid/${tag.id}/scan`, { status:newStatus });
  addLiveAuditEntry('📡','rfid',`RFID Scan — ${newStatus}`,`${tag.id} — ${tag.name}`,'RFID Reader');
  if (typeof _origSimRFID==='function') { _origSimRFID(tag); }
  else {
    tag.status = newStatus;
    const el = document.getElementById('tag-'+tag.id);
    if (el) { const b = el.querySelector('.badge'); if(b) { b.textContent=newStatus; b.className='badge '+(newStatus==='In Cabinet'?'badge-green':'badge-amber'); } }
    showToast(`📡 ${tag.id} — ${tag.name}: ${newStatus}`,'green');
  }
};

// ══════════════════════════════════════════════════════════════
// INTERCEPT: addLiveAuditEntry() — SAVE SA DB DIN
// ══════════════════════════════════════════════════════════════
const _origAudit = window.addLiveAuditEntry;
window.addLiveAuditEntry = function(icon, type, action, detail, user) {
  if (typeof _origAudit==='function') _origAudit(icon, type, action, detail, user);
  http.post('/api/audit', { icon, category:type, action, detail, user }).catch(()=>{});
};

// Reload audit log from DB and re-render
window.reloadAuditLog = async function() {
  const data = await http.get('/api/audit?limit=200');
  if (!data) { if (typeof renderAuditLog==='function') renderAuditLog(); return; }
  LIVE_AUDIT_LOGS.length = 0;
  data.forEach(a => {
    LIVE_AUDIT_LOGS.push({
      icon: a.icon||'📌', type: a.category||'general',
      action: a.action, detail: a.detail||'',
      user: a.user||'System', severity: 'ok',
      time: a.created_at ? new Date(a.created_at).toLocaleString('en-PH') : '—'
    });
  });
  if (typeof renderAuditLog==='function') renderAuditLog();
};

// INTERCEPT: deleteResident — call backend DELETE + audit
const _origDeleteResident = window.deleteResident;
window.deleteResident = async function(id) {
  const resident = RESIDENTS.find(r => r.id === id);
  const name = resident?.name || id;
  if (!confirm(`Burahin ang record ni ${name}? Hindi na ito mababawi.`)) return;
  await http.del(`/api/residents/${id}`);
  if (typeof _origDeleteResident === 'function') {
    // call original but skip its confirm (already confirmed)
    const idx = RESIDENTS.findIndex(r => r.id === id);
    if (idx > -1) {
      RESIDENTS.splice(idx, 1);
      delete RESIDENT_STATUS[id];
    }
    if (typeof renderResidentsTable==='function') renderResidentsTable();
    if (typeof refreshPopulationStats==='function') refreshPopulationStats();
  }
  addLiveAuditEntry('🗑️','record','Resident Record Deleted',`${id} — ${name}`, 'Staff');
  showToast(`Resident record ni ${name} ay natanggal.`,'');
};

// INTERCEPT: deleteIncident — call backend DELETE + audit
window.deleteIncident = async function(id) {
  const inc = INCIDENTS.find(x => x.id === id);
  if (!confirm(`Sigurado ka bang tanggalin ang incident report na ito? Hindi na ito mababawi.`)) return;
  await http.del(`/api/incidents/${id}`);
  const idx = INCIDENTS.findIndex(x => x.id === id);
  if (idx > -1) INCIDENTS.splice(idx, 1);
  addLiveAuditEntry('🗑️','incident','Incident Report Deleted',`${id} — ${inc?.type||''}`, 'Staff');
  showToast(`Incident report ${id} ay natanggal.`,'');
  if (typeof renderIncidents==='function') renderIncidents();
  if (typeof refreshDashboardStats==='function') refreshDashboardStats();
};

// ══════════════════════════════════════════════════════════════
// INTERCEPT: checkRequestStatus() — CHECK SA DB
// ══════════════════════════════════════════════════════════════
const _origCheckStatus = window.checkRequestStatus;
window.checkRequestStatus = async function(code) {
  if (!code?.trim()) { showToast('Ilagay ang confirmation code.','red'); return; }
  const upper = code.trim().toUpperCase();
  let req = CERT_REQUESTS.find(x => x.code.trim().toUpperCase()===upper);
  if (!req) {
    const fresh = await http.get('/api/cert-requests');
    if (fresh) { CERT_REQUESTS.length=0; fresh.map(dbToCertReq).forEach(r=>CERT_REQUESTS.push(r)); }
    req = CERT_REQUESTS.find(x => x.code.trim().toUpperCase()===upper);
  }
  if (typeof showRequestStatus==='function') showRequestStatus(req?req.code:null, req);
};

// ══════════════════════════════════════════════════════════════
// INTERCEPT: Update cert status from Kanban drag (if any button click)
// ══════════════════════════════════════════════════════════════
window.updateCertStatusDB = async function(code, status) {
  await http.put(`/api/cert-requests/${code}/status`, { status, user:'Staff' });
  const req = CERT_REQUESTS.find(r => r.code===code);
  if (req) req.status = status;
  if (typeof renderCertKanban==='function') renderCertKanban();
  addLiveAuditEntry('📋','cert',`Certificate → ${status}`,code,'Staff');
  showToast(`✅ ${code} — Status: ${status}`,'green');
};






// ══════════════════════════════════════════════════════════════
// Hook launchApp to load DB data after login + SAVE SESSION
// ══════════════════════════════════════════════════════════════
(function() {
  const _orig = window.launchApp;
  if (typeof _orig === 'function') {
    window.launchApp = function(name, role) {
      _orig(name, role);
      setTimeout(loadAllFromDB, 700);
      // Save session para hindi mag-logout kapag nag-refresh
      const access = (typeof currentUserAccess !== 'undefined') ? currentUserAccess : 'Full Access';
      sessionStorage.setItem('smartbrgy_loggedin', '1');
      sessionStorage.setItem('smartbrgy_user', name || 'Staff');
      sessionStorage.setItem('smartbrgy_role', role || 'Staff');
      sessionStorage.setItem('smartbrgy_access', access);
    };
  }
})();

// ══════════════════════════════════════════════════════════════
// AUTO-RESTORE SESSION KAPAG NAG-REFRESH
// ══════════════════════════════════════════════════════════════
window.addEventListener('DOMContentLoaded', function() {
  const isLoggedIn = sessionStorage.getItem('smartbrgy_loggedin');
  if (isLoggedIn === '1') {
    const loginScreen = document.getElementById('login-screen');
    const appEl = document.getElementById('app');
    if (loginScreen && appEl) {
      loginScreen.style.display = 'none';
      appEl.classList.add('visible');
      if (typeof window.facePassed !== 'undefined') window.facePassed = true;
      // Restore access control
      const savedUser   = sessionStorage.getItem('smartbrgy_user') || 'Staff';
      const savedRole   = sessionStorage.getItem('smartbrgy_role') || 'Staff';
      const savedAccess = sessionStorage.getItem('smartbrgy_access') || 'Full Access';
      if (typeof currentUserName !== 'undefined') currentUserName = savedUser;
      if (typeof currentUserRole !== 'undefined') currentUserRole = savedRole;
      if (typeof currentUserAccess !== 'undefined') currentUserAccess = savedAccess;
      if (typeof applyAccessControl === 'function') applyAccessControl(savedAccess);
      if (typeof runCounters === 'function') runCounters();
      if (typeof buildCharts === 'function') buildCharts();
      if (typeof startClock === 'function') startClock();
      if (typeof populateEligResidentDropdown === 'function') populateEligResidentDropdown(null);
      setTimeout(loadAllFromDB, 500);
    }
  }
});

// ══════════════════════════════════════════════════════════════
// HOOK doLogout — I-CLEAR ANG SESSION
// ══════════════════════════════════════════════════════════════
(function() {
  const _origLogout = window.doLogout;
  window.doLogout = function() {
    sessionStorage.removeItem('smartbrgy_loggedin');
    sessionStorage.removeItem('smartbrgy_user');
    localStorage.removeItem('smartbrgy_active_screen');
    sessionStorage.removeItem('smartbrgy_role');
    if (typeof _origLogout === 'function') _origLogout();
  };
})();

// ══════════════════════════════════════════════════════════════
// FIX: openViewResident — KUMPLETO NA ANG LAHAT NG DETAILS
// ══════════════════════════════════════════════════════════════
window.openViewResident = function(id) {
  window.currentViewResidentId = id;
  const r = RESIDENTS.find(x => x.id === id);
  if (!r) return;
  const rs = RESIDENT_STATUS[id];
  const age = (typeof calcAge === 'function') ? calcAge(r.dob) : '—';
  const senior = age >= 60;

  const blotterHtml = rs?.blotter
    ? `<div style="grid-column:1/-1;background:rgba(239,68,68,0.08);border:1px solid rgba(239,68,68,0.3);border-radius:var(--radius-sm);padding:10px 12px;font-size:12px;">
        <strong style="color:#FCA5A5;">⚠️ Blotter Record:</strong>
        <div style="color:var(--text-muted);margin-top:4px;">${(rs.blotterDetails||[]).join('<br>')}</div>
       </div>`
    : `<div style="grid-column:1/-1;background:var(--green-dim);border:1px solid var(--border-green);border-radius:var(--radius-sm);padding:8px 12px;font-size:12px;color:var(--green-500);">
        ✅ No blotter record — Good Standing
       </div>`;

  const seniorBadge = senior
    ? '<span class="badge badge-senior" style="margin-left:6px;">👴 Senior Citizen</span>' : '';

  const content = document.getElementById('view-resident-content');
  if (!content) return;

  content.innerHTML = `
    <div style="display:grid;grid-template-columns:1fr 1fr;gap:12px;">
      <div class="form-group">
        <div class="form-label">Resident ID</div>
        <div style="font-family:var(--font-mono);color:var(--blue-400);">${r.id || '—'}</div>
      </div>
      <div class="form-group">
        <div class="form-label">Status</div>
        <span class="badge ${r.status === 'Active' ? 'badge-green' : 'badge-red'}">${r.status || 'Active'}</span>
        ${seniorBadge}
      </div>
      <div class="form-group">
        <div class="form-label">Full Name</div>
        <div style="color:var(--text-primary);font-weight:600;">${r.name || '—'}</div>
      </div>
      <div class="form-group">
        <div class="form-label">Date of Birth</div>
        <div>${r.dob || '—'}</div>
      </div>
      <div class="form-group">
        <div class="form-label">Age</div>
        <div style="font-size:18px;font-weight:800;color:${senior ? 'var(--senior-color)' : 'var(--text-primary)'};">${age} years old</div>
      </div>
      <div class="form-group">
        <div class="form-label">Gender</div>
        <div>${r.gender || '—'}</div>
      </div>
      <div class="form-group">
        <div class="form-label">Civil Status</div>
        <div>${r.civil || '—'}</div>
      </div>
      <div class="form-group">
        <div class="form-label">Zone / Purok</div>
        <div>${r.purok || '—'}</div>
      </div>
      <div class="form-group">
        <div class="form-label">Household</div>
        <div>${r.household || '—'}</div>
      </div>
      <div class="form-group">
        <div class="form-label">Contact</div>
        <div>${r.contact || '—'}</div>
      </div>
      <div class="form-group">
        <div class="form-label">Residency Type</div>
        <div>${r.type || '—'}</div>
      </div>
      ${blotterHtml}
    </div>`;

  if (typeof openModal === 'function') openModal('modal-view-resident');
};

// ══════════════════════════════════════════════════════════════
// OVERRIDE: renderPurokCards — Dagdag Edit & Delete buttons
// ══════════════════════════════════════════════════════════════
const _origRenderPurokCards = window.renderPurokCards;
window.renderPurokCards = function() {
  // Run the original first to build the grid
  if (typeof _origRenderPurokCards === 'function') _origRenderPurokCards();
  // Then inject Edit + Delete buttons into each card
  const grid = document.getElementById('demo-purok-grid');
  if (!grid) return;
  // Rebuild grid with buttons (override innerHTML approach)
  const countByPurok = {};
  const seniorByPurok = {};
  const pwdByPurok = {};
  const beneByPurok = {};
  RESIDENTS.forEach(r => {
    countByPurok[r.purok] = (countByPurok[r.purok] || 0) + 1;
    if (typeof isSenior === 'function' && isSenior(r.dob)) seniorByPurok[r.purok] = (seniorByPurok[r.purok] || 0) + 1;
    const groups = (typeof getResidentGroups === 'function') ? getResidentGroups(r) : (r.specialGroups || []);
    if (groups.includes('PWD')) pwdByPurok[r.purok] = (pwdByPurok[r.purok] || 0) + 1;
    if (groups.includes('4Ps Beneficiary')) beneByPurok[r.purok] = (beneByPurok[r.purok] || 0) + 1;
  });
  const total = RESIDENTS.length;
  grid.innerHTML = '';
  PUROK_DATA.forEach(p => {
    const count = countByPurok[p.key] || 0;
    const pct = total > 0 ? ((count / total) * 100).toFixed(1) : '0.0';
    const barPct = total > 0 ? (count / total * 100) : 0;
    const seniors = seniorByPurok[p.key] || 0;
    const pwd = pwdByPurok[p.key] || 0;
    const bene = beneByPurok[p.key] || 0;
    const esc = (typeof escapeText === 'function') ? escapeText : (v => String(v));
    const keyEsc = esc(p.key).replace(/'/g, "\\'");
    grid.innerHTML += `
      <div class="demo-purok-card" style="display:flex;flex-direction:column;">
        <div class="demo-purok-name">📍 ${esc(p.label)}</div>
        <div class="demo-purok-pop" style="color:${p.color};">${count.toLocaleString()}</div>
        <div class="demo-purok-pct">${pct}% ng kabuuang populasyon</div>
        <div class="demo-purok-bar" style="margin:8px 0 6px;">
          <div class="progress-bar"><div class="progress-fill" style="width:${barPct}%;background:${p.color};"></div></div>
        </div>
        <div class="sg-tags" style="flex:1;">
          ${seniors > 0 ? `<span class="demo-purok-tag" style="color:var(--senior-color);border-color:rgba(245,158,11,0.25);">👴 ${seniors} Seniors</span>` : ''}
          ${pwd > 0     ? `<span class="demo-purok-tag" style="color:#A78BFA;border-color:rgba(139,92,246,0.25);">♿ ${pwd} PWD</span>` : ''}
          ${bene > 0    ? `<span class="demo-purok-tag" style="color:#EF4444;border-color:rgba(239,68,68,0.25);">💰 ${bene} 4Ps</span>` : ''}
        </div>
        <div style="display:flex;gap:6px;margin-top:10px;padding-top:8px;border-top:1px solid var(--border);">
          <button class="btn btn-xs btn-primary" onclick="openEditPurok('${keyEsc}')" style="flex:1;font-size:10.5px;">✏️ Edit</button>
          <button class="btn btn-xs" onclick="deletePurok('${keyEsc}')" style="flex:1;font-size:10.5px;background:rgba(239,68,68,0.08);border-color:rgba(239,68,68,0.3);color:#FCA5A5;">🗑️ Delete</button>
        </div>
      </div>`;
  });
};

// ══════════════════════════════════════════════════════════════
// PUROK EDIT & DELETE — DB-BACKED
// ══════════════════════════════════════════════════════════════

window.openEditPurok = function(keyName) {
  const p = PUROK_DATA.find(x => x.key === keyName);
  if (!p) return;
  const modal = document.getElementById('modal-purok');
  const nameEl = document.getElementById('purok-name');
  if (nameEl) { nameEl.value = p.key; nameEl.disabled = true; }
  const labelEl = document.getElementById('purok-label');
  if (labelEl) { labelEl.value = p.label || p.key; labelEl.disabled = false; }
  const colorEl = document.getElementById('purok-color');
  if (colorEl) colorEl.value = p.color && p.color.startsWith('#') ? p.color : '#22C55E';
  if (modal) modal.dataset.editKey = p.key;
  const title = modal?.querySelector('.modal-title');
  if (title) title.textContent = '✏️ I-edit ang Purok';
  const saveBtn = modal?.querySelector('button.btn-green');
  if (saveBtn) saveBtn.textContent = '💾 I-update ang Purok';
  if (typeof openModal === 'function') openModal('modal-purok');
};

window.openAddPurok = function() {
  const modal = document.getElementById('modal-purok');
  if (modal) delete modal.dataset.editKey;
  const title = modal?.querySelector('.modal-title');
  if (title) title.textContent = '🏘️ Add Purok';
  const saveBtn = modal?.querySelector('button.btn-green');
  if (saveBtn) saveBtn.textContent = '💾 Save Purok';
  const nameEl = document.getElementById('purok-name');
  if (nameEl) { nameEl.value = ''; nameEl.disabled = false; }
  const labelEl = document.getElementById('purok-label');
  if (labelEl) { labelEl.value = ''; labelEl.disabled = false; }
  const colorEl = document.getElementById('purok-color');
  if (colorEl) colorEl.value = '#22C55E';
  if (typeof openModal === 'function') openModal('modal-purok');
};

window.savePurok = async function() {
  const modal = document.getElementById('modal-purok');
  const editKey = modal?.dataset?.editKey;
  if (editKey) {
    // ── EDIT mode ──
    const colorVal = document.getElementById('purok-color')?.value || '#22C55E';
    const labelVal = (document.getElementById('purok-label')?.value || '').trim();
    const p = PUROK_DATA.find(x => x.key === editKey);
    if (!p) return;
    if (!labelVal) { showToast('❌ Ilagay ang Display Name.', 'red'); return; }
    const newLabel = labelVal || p.label;
    const result = await http.put(`/api/purok/${encodeURIComponent(editKey)}`, {
      label: newLabel, color: colorVal, by: 'Staff'
    });
    if (result && !result.error) {
      p.color = colorVal;
      p.label = newLabel;
      addLiveAuditEntry('✏️','record','Purok Updated', editKey, 'Staff');
      showToast(`✅ "${editKey}" na-update!`, 'green');
      delete modal.dataset.editKey;
      if (typeof closeModal === 'function') closeModal('modal-purok');
      const nameEl2 = document.getElementById('purok-name');
      if (nameEl2) nameEl2.disabled = false;
      if (typeof renderDemographics === 'function') renderDemographics();
      if (typeof renderDashPurokBreakdown === 'function') renderDashPurokBreakdown();
      if (typeof syncPurokSelects === 'function') syncPurokSelects();
    } else {
      showToast(`❌ ${result?.error || 'Hindi ma-update. Siguraduhing tumatakbo ang server.'}`, 'red');
    }
  } else {
    // ── ADD mode ──
    const nameEl  = document.getElementById('purok-name');
    const labelEl = document.getElementById('purok-label');
    const colorEl = document.getElementById('purok-color');
    const key   = (nameEl?.value || '').trim();
    const label = (labelEl?.value || '').trim() || key;
    const color = colorEl?.value || '#22C55E';
    if (!key) { showToast('❌ Ilagay ang Purok ID.', 'red'); return; }
    if (!label) { showToast('❌ Ilagay ang Display Name ng Purok.', 'red'); return; }
    if (PUROK_DATA.some(p => p.key.toLowerCase() === key.toLowerCase())) {
      showToast('❌ Mayroon na itong Purok ID. Pumili ng ibang ID.', 'red'); return;
    }
    const result = await http.post('/api/purok', { key_name: key, label, color, total: 0, pct: 0, by: 'Staff' });
    if (result && !result.error) {
      PUROK_DATA.push({ key, label, total: 0, color, pct: 0 });
      if (typeof syncPurokSelects === 'function') syncPurokSelects();
      if (typeof persistCustomPuroks === 'function') persistCustomPuroks();
      addLiveAuditEntry('🏘️','record','Purok Added', `${key} — ${label}`, 'Staff');
      showToast(`✅ "${label}" na-add na!`, 'green');
      if (typeof closeModal === 'function') closeModal('modal-purok');
      if (typeof renderDemographics === 'function') renderDemographics();
      if (typeof renderDashPurokBreakdown === 'function') renderDashPurokBreakdown();
    } else {
      const errMsg = result?.error || 'Hindi ma-add ang purok. Siguraduhing tumatakbo ang server (python app.py).';
      showToast(`❌ ${errMsg}`, 'red');
    }
  }
};

window.deletePurok = async function(keyName) {
  if (!confirm(`Burahin ang "${keyName}"?\nHindi ito mababawi.`)) return;
  const result = await http.del(`/api/purok/${encodeURIComponent(keyName)}`);
  if (result && !result.error) {
    const idx = PUROK_DATA.findIndex(p => p.key === keyName);
    if (idx > -1) PUROK_DATA.splice(idx, 1);
    if (typeof syncPurokSelects === 'function') syncPurokSelects();
    addLiveAuditEntry('🗑️','record','Purok Deleted', keyName, 'Staff');
    showToast(`🗑️ "${keyName}" nabura na.`, 'green');
    if (typeof renderDemographics === 'function') renderDemographics();
    if (typeof renderDashPurokBreakdown === 'function') renderDashPurokBreakdown();
  } else {
    showToast(`❌ ${result?.error || 'Hindi mabura.'}`, 'red');
  }
};

// ══════════════════════════════════════════════════════════════
// REALTIME AUTO-REFRESH — Bawat 30 segundo
// ══════════════════════════════════════════════════════════════
(function startRealtimeRefresh() {
  let busy = false;
  setInterval(async () => {
    if (busy) return;
    const appEl = document.getElementById('app');
    if (!appEl?.classList.contains('visible')) return;
    busy = true;
    try {
      const data = await http.get('/api/residents');
      if (!data) return;
      const mapped = data.map(dbToResident);
      RESIDENTS.length = 0; mapped.forEach(r => RESIDENTS.push(r));
      const ns = rebuildStatus(mapped);
      Object.keys(ns).forEach(k => { RESIDENT_STATUS[k] = ns[k]; });
      // Recompute purok totals
      PUROK_DATA.forEach(p => {
        p.total = RESIDENTS.filter(r => r.purok === p.key && r.status === 'Active').length;
      });
      const totalActive = RESIDENTS.filter(r => r.status === 'Active').length;
      PUROK_DATA.forEach(p => {
        p.pct = totalActive > 0 ? Math.round((p.total / totalActive) * 100) : 0;
      });
      if (typeof renderDemographics === 'function') renderDemographics();
      if (typeof renderDashPurokBreakdown === 'function') renderDashPurokBreakdown();
      if (typeof refreshPopulationStats === 'function') refreshPopulationStats();
      // Silently update counter elements
      document.querySelectorAll('.counter[data-target]').forEach(el => {
        const label = el.closest('.stat-card')?.querySelector('.stat-label')?.textContent || '';
        if (label.includes('Population') || label.includes('Resident')) {
          el.dataset.target = totalActive;
          el.textContent = totalActive.toLocaleString();
        }
      });
    } catch(e) {
      console.warn('Auto-refresh error:', e);
    } finally {
      busy = false;
    }
  }, 30000);
})();

// ══════════════════════════════════════════════════════════════
// FILE PREVIEW HELPERS — Portal & Incident attachments
// ══════════════════════════════════════════════════════════════
document.addEventListener('change', function(e) {
  // Portal attachment preview
  if (e.target.id === 'portal-attachment') {
    const preview = document.getElementById('portal-attachment-preview');
    if (!preview) return;
    const file = e.target.files?.[0];
    if (!file) { preview.style.display = 'none'; preview.innerHTML = ''; return; }
    preview.style.display = 'block';
    if (file.type.startsWith('image/')) {
      const url = URL.createObjectURL(file);
      preview.innerHTML = `<img src="${url}" style="max-height:80px;border-radius:6px;border:1px solid var(--border);"/>`;
    } else {
      preview.innerHTML = `<span style="font-size:12px;color:var(--text-muted);">📎 ${file.name}</span>`;
    }
  }
  // Incident attachments preview
  if (e.target.id === 'inc-attachments') {
    const preview = document.getElementById('inc-attachments-preview');
    if (!preview) return;
    preview.innerHTML = '';
    Array.from(e.target.files || []).forEach(file => {
      if (file.type.startsWith('image/')) {
        const url = URL.createObjectURL(file);
        const img = document.createElement('img');
        img.src = url;
        img.style.cssText = 'max-height:60px;border-radius:6px;border:1px solid var(--border);';
        preview.appendChild(img);
      } else {
        const span = document.createElement('span');
        span.style.cssText = 'font-size:12px;color:var(--text-muted);';
        span.textContent = `📎 ${file.name}`;
        preview.appendChild(span);
      }
    });
  }
});

console.log('📡 SmartBrgy DB Connector v2 loaded. Backend:', _DB_API);
