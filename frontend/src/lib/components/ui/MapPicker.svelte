<script lang="ts">
  import { onMount, onDestroy } from 'svelte';

  let {
    lat = -23.5505,
    lng = -46.6333,
    onchange,
  }: {
    lat?: number;
    lng?: number;
    onchange: (lat: number, lng: number) => void;
  } = $props();

  let mapEl: HTMLDivElement;
  let map: any;
  let marker: any;
  let currentLat = $state(lat);
  let currentLng = $state(lng);

  let cep        = $state('');
  let buscando   = $state(false);
  let erroCep    = $state('');

  onMount(async () => {
    const L = (await import('leaflet')).default;
    await import('leaflet/dist/leaflet.css');

    delete (L.Icon.Default.prototype as any)._getIconUrl;
    L.Icon.Default.mergeOptions({
      iconRetinaUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon-2x.png',
      iconUrl:       'https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon.png',
      shadowUrl:     'https://unpkg.com/leaflet@1.9.4/dist/images/marker-shadow.png',
    });

    map = L.map(mapEl).setView([currentLat, currentLng], 13);

    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
      attribution: '© <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>',
      maxZoom: 19,
    }).addTo(map);

    marker = L.marker([currentLat, currentLng], { draggable: true }).addTo(map);

    function update(latlng: { lat: number; lng: number }) {
      currentLat = parseFloat(latlng.lat.toFixed(6));
      currentLng = parseFloat(latlng.lng.toFixed(6));
      onchange(currentLat, currentLng);
    }

    map.on('click', (e: any) => {
      marker.setLatLng(e.latlng);
      update(e.latlng);
    });

    marker.on('dragend', () => update(marker.getLatLng()));
  });

  onDestroy(() => { map?.remove(); });

  async function buscarCep() {
    const cepLimpo = cep.replace(/\D/g, '');
    if (cepLimpo.length !== 8) {
      erroCep = 'CEP deve ter 8 dígitos.';
      return;
    }
    erroCep = '';
    buscando = true;
    try {
      // 1. Busca endereço pelo ViaCEP
      const viacep = await fetch(`https://viacep.com.br/ws/${cepLimpo}/json/`);
      const addr   = await viacep.json();
      if (addr.erro) { erroCep = 'CEP não encontrado.'; return; }

      // 2. Geocodifica com Nominatim usando logradouro + cidade + UF
      const query   = encodeURIComponent(`${addr.logradouro || ''}, ${addr.bairro || ''}, ${addr.localidade}, ${addr.uf}, Brasil`);
      const geo     = await fetch(`https://nominatim.openstreetmap.org/search?q=${query}&format=json&limit=1&countrycodes=br`, {
        headers: { 'Accept-Language': 'pt-BR' },
      });
      const results = await geo.json();

      if (!results.length) {
        // Fallback: busca só pela cidade/UF
        const q2  = encodeURIComponent(`${addr.localidade}, ${addr.uf}, Brasil`);
        const geo2 = await fetch(`https://nominatim.openstreetmap.org/search?q=${q2}&format=json&limit=1&countrycodes=br`);
        const r2   = await geo2.json();
        if (!r2.length) { erroCep = 'Não foi possível localizar o endereço no mapa.'; return; }
        results.push(...r2);
      }

      const { lat: newLat, lon: newLon } = results[0];
      const newLatF = parseFloat(parseFloat(newLat).toFixed(6));
      const newLngF = parseFloat(parseFloat(newLon).toFixed(6));

      currentLat = newLatF;
      currentLng = newLngF;
      onchange(currentLat, currentLng);

      if (map && marker) {
        map.setView([newLatF, newLngF], 16);
        marker.setLatLng([newLatF, newLngF]);
      }
    } catch {
      erroCep = 'Erro ao buscar CEP. Verifique sua conexão.';
    } finally {
      buscando = false;
    }
  }

  function onCepInput(e: Event) {
    const raw = (e.currentTarget as HTMLInputElement).value.replace(/\D/g, '').slice(0, 8);
    cep = raw.length > 5 ? raw.slice(0, 5) + '-' + raw.slice(5) : raw;
  }

  function onCepKeydown(e: KeyboardEvent) {
    if (e.key === 'Enter') { e.preventDefault(); buscarCep(); }
  }
</script>

<!-- Busca por CEP -->
<div style="display:flex; gap:8px; margin-bottom:10px; align-items:flex-start;">
  <div style="flex:1;">
    <div style="display:flex; gap:6px;">
      <input
        type="text"
        placeholder="CEP (ex: 04101-300)"
        value={cep}
        oninput={onCepInput}
        onkeydown={onCepKeydown}
        maxlength="9"
        style="
          flex:1; padding:8px 10px; border-radius:8px;
          background:#0f172a; border:1px solid rgba(255,255,255,0.1);
          color:#e2e8f0; font-size:13px; font-family:inherit;
        "
      />
      <button
        type="button"
        onclick={buscarCep}
        disabled={buscando}
        style="
          padding:8px 14px; border-radius:8px; cursor:pointer;
          background:rgba(52,211,153,0.12); border:1px solid rgba(52,211,153,0.3);
          color:#34d399; font-size:13px; font-family:inherit;
          transition:all .14s; white-space:nowrap;
          opacity:{buscando ? '0.6' : '1'};
        "
      >
        {buscando ? 'Buscando…' : 'Localizar'}
      </button>
    </div>
    {#if erroCep}
      <p style="font-size:11px; color:#f87171; margin:4px 0 0;">{erroCep}</p>
    {/if}
  </div>
</div>

<!-- Mapa -->
<div bind:this={mapEl} style="height:300px; width:100%; border-radius:10px; overflow:hidden; border:1px solid rgba(255,255,255,0.07);"></div>
<p style="font-size:11px; color:#475569; margin-top:6px; display:flex; align-items:center; gap:6px;">
  <svg width="12" height="12" viewBox="0 0 12 12" fill="none" style="flex-shrink:0">
    <circle cx="6" cy="6" r="5" stroke="#475569" stroke-width="1.2"/>
    <path d="M6 4v2.5M6 8h.01" stroke="#475569" stroke-width="1.2" stroke-linecap="round"/>
  </svg>
  Clique no mapa ou arraste o marcador para ajustar.
  Coordenadas: <strong style="color:#64748b;">{currentLat}, {currentLng}</strong>
</p>
