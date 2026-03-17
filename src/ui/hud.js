import { STATES } from '../constants.js';

const STATUS_LABELS = {
  [STATES.MATERIALIZING]: 'INITIALIZING',
  [STATES.IDLE]: 'STANDBY',
  [STATES.THINKING]: 'THINKING',
  [STATES.SPEAKING]: 'SPEAKING',
  [STATES.GLITCH]: 'ERROR',
  [STATES.POWERING_DOWN]: 'SHUTTING DOWN',
  [STATES.SLEEPING]: 'SLEEPING',
};

const STATUS_COLORS = {
  [STATES.MATERIALIZING]: '#33AAFF',
  [STATES.IDLE]: '#0D8BFF',
  [STATES.THINKING]: '#FFAA33',
  [STATES.SPEAKING]: '#33FF88',
  [STATES.GLITCH]: '#FF3333',
  [STATES.POWERING_DOWN]: '#666666',
  [STATES.SLEEPING]: '#333333',
};

export function initHud() {
  const hud = document.getElementById('hud');

  // Top left: title + drag region
  const topLeft = document.createElement('div');
  topLeft.id = 'hud-top-left';
  topLeft.setAttribute('data-tauri-drag-region', '');
  topLeft.style.cssText = 'position:absolute;top:16px;left:16px;pointer-events:auto;cursor:grab;';

  const title = document.createElement('div');
  title.style.cssText = 'font-size:14px;letter-spacing:3px;opacity:0.8;';
  title.textContent = 'NOVA v0.1.0';
  topLeft.appendChild(title);

  const subtitle = document.createElement('div');
  subtitle.style.cssText = 'font-size:10px;letter-spacing:2px;opacity:0.4;margin-top:2px;';
  subtitle.textContent = 'Neural Operative Virtual Assistant';
  topLeft.appendChild(subtitle);

  hud.appendChild(topLeft);

  // Top right: status
  const topRight = document.createElement('div');
  topRight.style.cssText = 'position:absolute;top:16px;right:16px;text-align:right;';

  const statusRow = document.createElement('div');
  statusRow.style.cssText = 'display:flex;align-items:center;gap:6px;justify-content:flex-end;';

  const dot = document.createElement('span');
  dot.id = 'status-dot';
  dot.style.cssText = 'width:8px;height:8px;border-radius:50%;display:inline-block;';
  statusRow.appendChild(dot);

  const label = document.createElement('span');
  label.id = 'status-label';
  label.style.cssText = 'font-size:11px;letter-spacing:2px;opacity:0.7;';
  statusRow.appendChild(label);

  topRight.appendChild(statusRow);

  const ollamaEl = document.createElement('div');
  ollamaEl.id = 'ollama-status';
  ollamaEl.style.cssText = 'font-size:9px;opacity:0.3;margin-top:4px;';
  topRight.appendChild(ollamaEl);

  hud.appendChild(topRight);

  // Log area
  const logArea = document.createElement('div');
  logArea.id = 'log-area';
  logArea.style.cssText = 'position:absolute;bottom:80px;left:16px;right:16px;max-height:200px;overflow-y:auto;pointer-events:auto;font-size:12px;line-height:1.6;opacity:0.7;';
  hud.appendChild(logArea);

  // Chat input
  const inputArea = document.createElement('div');
  inputArea.style.cssText = 'position:absolute;bottom:16px;left:16px;right:16px;pointer-events:auto;';

  const input = document.createElement('input');
  input.id = 'chat-input';
  input.type = 'text';
  input.placeholder = 'Talk to NOVA...';
  input.autocomplete = 'off';
  input.spellcheck = false;
  input.style.cssText = "width:100%;padding:10px 14px;background:rgba(13,139,255,0.08);border:1px solid rgba(13,139,255,0.3);border-radius:4px;color:#0D8BFF;font-family:'Courier New',monospace;font-size:13px;outline:none;letter-spacing:1px;";
  inputArea.appendChild(input);

  hud.appendChild(inputArea);

  updateStatus(STATES.MATERIALIZING);
}

export function updateStatus(state) {
  const dot = document.getElementById('status-dot');
  const label = document.getElementById('status-label');
  if (dot) dot.style.backgroundColor = STATUS_COLORS[state] || '#0D8BFF';
  if (label) label.textContent = STATUS_LABELS[state] || 'UNKNOWN';
}

export function setOllamaStatus(online) {
  const el = document.getElementById('ollama-status');
  if (el) {
    el.textContent = online ? 'OLLAMA CONNECTED' : 'OLLAMA OFFLINE';
    el.style.color = online ? '#33FF88' : '#FF3333';
  }
}

export function appendLog(text, sender) {
  sender = sender || 'nova';
  const log = document.getElementById('log-area');
  if (!log) return;

  const line = document.createElement('div');
  line.style.opacity = sender === 'user' ? '0.5' : '0.8';
  line.style.color = sender === 'user' ? '#1A6AAA' : '#0D8BFF';
  line.textContent = sender === 'user' ? '> ' + text : text;
  log.appendChild(line);

  while (log.children.length > 20) {
    log.removeChild(log.firstChild);
  }

  log.scrollTop = log.scrollHeight;
}

export function getChatInput() {
  return document.getElementById('chat-input');
}
