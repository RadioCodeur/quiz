export const STORAGE_KEY = 'a-lecoute.session.v1';
export const SETTINGS_KEY = 'a-lecoute.settings.v1';

// Include educational content so a changed answer or explanation invalidates old sessions.
export function bankSignature(bank) {
  let hash = 2166136261;
  for (const char of JSON.stringify(bank)) hash = Math.imul(hash ^ char.charCodeAt(0), 16777619) >>> 0;
  return hash.toString(16);
}

export function validateSession(s, bank) {
  if (!s || s.version !== 1 || !['normal', 'errors'].includes(s.mode) || !Array.isArray(s.questionIds) || !s.questionIds.length || s.questionIds.length > 200) return false;
  if (new Set(s.questionIds).size !== s.questionIds.length || !Number.isInteger(s.index) || s.index < 0 || s.index >= s.questionIds.length || typeof s.completed !== 'boolean') return false;
  if (!s.optionOrders || typeof s.optionOrders !== 'object' || !s.answers || typeof s.answers !== 'object' || Array.isArray(s.answers)) return false;
  const byId = new Map(bank.map(q => [q.id, q]));
  if (Object.keys(s.answers).some(id => !s.questionIds.includes(id))) return false;
  return s.questionIds.every((id, index) => {
    const q = byId.get(id), order = s.optionOrders[id], answer = s.answers[id];
    if (!q || !Array.isArray(order) || order.length !== 4 || new Set(order).size !== 4 || !order.every(o => q.options.some(option => option.id === o))) return false;
    if (answer !== undefined && !q.options.some(o => o.id === answer)) return false;
    if (index < s.index && answer === undefined) return false;
    if (index > s.index && answer !== undefined) return false;
    return !s.completed || (s.index === s.questionIds.length - 1 && answer !== undefined);
  });
}

export function createStorage(getStorage = () => globalThis.localStorage) {
  let available = true;
  const read = key => {
    let raw;
    try { raw = getStorage().getItem(key); } catch { available = false; return null; }
    try { return JSON.parse(raw); } catch { return { invalidJSON: true }; }
  };
  const write = (key, value) => { try { getStorage().setItem(key, JSON.stringify(value)); } catch { available = false; } };
  const remove = key => { try { getStorage().removeItem(key); } catch { available = false; } };
  return {
    get available() { return available; },
    read, write, remove,
    saveSession(session, signature) { write(STORAGE_KEY, { signature, session }); },
    loadSession(bank, signature) {
      const saved = read(STORAGE_KEY);
      if (!saved) return { session: null, discarded: false };
      if (saved.signature !== signature || !validateSession(saved.session, bank)) {
        remove(STORAGE_KEY);
        return { session: null, discarded: true };
      }
      return { session: saved.session, discarded: false };
    },
  };
}
