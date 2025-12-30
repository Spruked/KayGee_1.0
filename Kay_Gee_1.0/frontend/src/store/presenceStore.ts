// Placeholder to prevent import errors
export const PresenceStore = {
  get: () => ({ authority: 'observer', visibility: 'latent', resonance: 0 }),
  set: (next: any) => console.log('PresenceStore.set called:', next),
  subscribe: (_fn: any) => () => {}
};