// integration/plug-in-loader.js
// KayGee Orb Auto-Loader v3.1
(function() {
  if (window.KayGeeInitialized) return;
  window.KayGeeInitialized = true;

  // Configuration from meta tags or defaults
  const config = {
    appId: document.querySelector('meta[name="kaygee-app-id"]')?.content ||
           window.location.hostname.replace(/\./g, '-'),
    domain: document.querySelector('meta[name="kaygee-domain"]')?.content || 'general',
    permissions: (document.querySelector('meta[name="kaygee-permissions"]')?.content || 'escalate_to_orb')
                 .split(',').map(p => p.trim()),
    ucmEndpoint: document.querySelector('meta[name="kaygee-ucm"]')?.content || 'ws://localhost:8000/ws/ucm'
  };

  // Load main bundle
  const script = document.createElement('script');
  script.src = 'https://cdn.kaygee.ai/orb/v3.1/orb-bundle.min.js';

  script.onload = () => {
    const container = document.createElement('div');
    container.id = 'kaygee-orb-container';
    document.body.appendChild(container);

    window.KayGeeOrb = new window.KayGeeOrbComponent(container, config);
    console.log('🌌 KayGee Orb initialized:', config.appId);
  };

  script.onerror = () => {
    console.error('❌ Failed to load KayGee Orb. Check CDN endpoint.');
  };

  document.head.appendChild(script);
})();