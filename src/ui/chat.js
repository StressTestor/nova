import { invoke } from '@tauri-apps/api/core';
import { listen } from '@tauri-apps/api/event';
import { appendLog, updateStatus, setOllamaStatus, getChatInput } from './hud.js';
import { setState, triggerGlitch } from '../renderer/animation.js';

let currentResponse = '';

export async function initChat() {
  const input = getChatInput();
  if (!input) return;

  let lastSend = 0;
  input.addEventListener('keydown', async (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      const now = Date.now();
      if (now - lastSend < 300) return;
      lastSend = now;

      const text = input.value.trim();
      if (!text) return;

      input.value = '';
      await sendMessage(text);
    }
  });

  await listen('llm_token', (event) => {
    const payload = event.payload;
    if (payload.done) {
      if (currentResponse) {
        appendLog(currentResponse, 'nova');
      }
      currentResponse = '';
    } else {
      currentResponse += payload.token;
    }
  });

  await listen('llm_interrupted', () => {
    if (currentResponse) {
      appendLog(currentResponse + ' [interrupted]', 'nova');
    }
    currentResponse = '';
  });

  await listen('state_change', (event) => {
    updateStatus(event.payload);
    setState(event.payload);
  });

  await listen('ollama_status', (event) => {
    setOllamaStatus(event.payload === 'online');
  });

  try {
    const online = await invoke('get_llm_status');
    setOllamaStatus(online);
  } catch (e) {
    setOllamaStatus(false);
  }
}

async function sendMessage(text) {
  appendLog(text, 'user');
  currentResponse = '';

  try {
    const result = await invoke('send_message', { text: text });
    if (result && !currentResponse) {
      appendLog(result, 'nova');
    }
  } catch (err) {
    appendLog('Error: ' + err, 'nova');
    triggerGlitch();
  }
}
