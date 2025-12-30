// DEBUG: Step 1 - Test event firing
window.addEventListener('user-request-escalation', e => {
  console.log('🔥 ESCALATION EVENT CAUGHT', e.detail);
});

// DEBUG: Step 4 - Manual PresenceStore test
import { PresenceStore } from './src/store/presenceStore.js';

// Function to test manual state change
window.testPresenceStore = () => {
  console.log('🧪 Testing PresenceStore mutation...');
  PresenceStore.set({
    visibility: 'manifested',
    cognition: 'reasoning',
    resonance: 0.62,
    authority: 'supervisory',
    focus: 'escalated'
  });
  console.log('✅ PresenceStore.set() called');
};

// Function to check current state
window.checkPresenceState = () => {
  const state = PresenceStore.get();
  console.log('📊 Current Presence State:', state);
  return state;
};

// Function to trigger escalation
window.triggerEscalation = () => {
  console.log('🚀 Triggering escalation...');
  window.dispatchEvent(new CustomEvent('user-request-escalation', {
    detail: {
      appId: 'dashboard-app',
      context: { confidence: 0.62, reason: 'manual escalation test' }
    }
  }));
};