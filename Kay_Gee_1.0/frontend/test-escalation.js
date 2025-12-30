// Test script for escalation
console.log('Testing KayGee Orb Escalation...');

// Trigger escalation event
window.dispatchEvent(new CustomEvent('user-request-escalation', {
  detail: {
    appId: 'test-app',
    context: { confidence: 0.62, reason: 'manual escalation test' }
  }
}));

console.log('Escalation event dispatched. Check console for PresenceStore logs.');