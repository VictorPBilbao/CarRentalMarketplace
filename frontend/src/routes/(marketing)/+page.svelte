<script lang="ts">
  import './home.css';
  import { onMount } from 'svelte';
  import logoImage from '$lib/assets/logo.jpeg';

  let scrollY = $state(0);
  let sectionsVisible = $state<Record<string, boolean>>({});

  onMount(() => {
    const observer = new IntersectionObserver(
      (entries) => {
        entries.forEach(entry => {
          if (entry.isIntersecting) {
            sectionsVisible[(entry.target as HTMLElement).dataset.section!] = true;
          }
        });
      },
      { threshold: 0.1 }
    );

    document.querySelectorAll('[data-section]').forEach(el => observer.observe(el));
    return () => observer.disconnect();
  });
</script>

<svelte:window bind:scrollY />

<svelte:head>
  <title>CarRental Marketplace — A ponte entre locadoras</title>
  <link rel="preconnect" href="https://fonts.googleapis.com" />
  <link href="https://fonts.googleapis.com/css2?family=Instrument+Serif:ital@0;1&family=DM+Sans:opsz,wght@9..40,300;9..40,400;9..40,500&display=swap" rel="stylesheet" />
</svelte:head>

<!-- NAV -->
<nav class:scrolled={scrollY > 40}>
  <div class="nav-inner">
    <a href="/" class="logo">
      <span class="logo-icon">◈</span>
      CarRental
    </a>
    <div class="nav-links">
      <a href="#como-funciona">Como funciona</a>
      <a href="#para-quem">Para quem</a>
      <a href="#contato">Contato</a>
    </div>
    <div class="nav-actions">
      <a href="/login" class="btn-ghost">Entrar</a>
      <a href="/cadastro" class="btn-primary">Cadastrar locadora</a>
    </div>
  </div>
</nav>

<!-- HERO -->
<section class="hero">
  <div class="hero-bg" aria-hidden="true">
    <div class="grid-lines"></div>
    <div class="orb orb-1"></div>
    <div class="orb orb-2"></div>
    <div class="orb orb-3"></div>
  </div>

  <div class="hero-inner">
    <div class="hero-content">
      <div class="hero-badge">
        <span class="badge-dot"></span>
        Plataforma B2B para locadoras de veículos
      </div>

      <h1>
        Sua frota,<br />
        <em>nas maiores</em><br />
        locadoras do país
      </h1>

      <p class="hero-sub">
        O CarRental conecta pequenas locadoras às grandes redes através de uma API padronizada.
        Cadastre seus veículos uma vez, alcance clientes em todo o Brasil.
      </p>

      <div class="hero-cta">
        <a href="/locadora/cadastro" class="cta-main">
          Começar agora
          <svg width="16" height="16" viewBox="0 0 16 16" fill="none" aria-hidden="true">
            <path d="M3 8h10M9 4l4 4-4 4" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
          </svg>
        </a>
        <a href="#como-funciona" class="cta-link">Ver como funciona</a>
      </div>

      <div class="hero-stats">
        <div class="stat">
          <span class="stat-num">+200</span>
          <span class="stat-label">Locadoras parceiras</span>
        </div>
        <div class="stat-div"></div>
        <div class="stat">
          <span class="stat-num">+15k</span>
          <span class="stat-label">Veículos na plataforma</span>
        </div>
        <div class="stat-div"></div>
        <div class="stat">
          <span class="stat-num">8</span>
          <span class="stat-label">Grandes redes integradas</span>
        </div>
      </div>
    </div>

    <div class="hero-visual">
      <div class="dashboard-card">
        <div class="card-topbar">
          <span></span><span></span><span></span>
        </div>
        <div class="card-body">
          <div class="card-header">
            <div>
              <p class="card-sublabel">Sua frota hoje</p>
              <p class="card-big">142 veículos</p>
            </div>
            <span class="badge-green">↑ 12% este mês</span>
          </div>

          <div class="car-list">
            {#each [
              { name: 'SUV Premium', active: true },
              { name: 'Sedan Executivo', active: true },
              { name: 'Hatch Econômico', active: true },
              { name: 'Pickup 4x4', active: false }
            ] as car}
              <div class="car-row">
                <span class="car-dot" class:active={car.active}></span>
                <span class="car-name">{car.name}</span>
                <span class="car-badge" class:disponivel={car.active}>
                  {car.active ? 'Disponível' : 'Alugado'}
                </span>
              </div>
            {/each}
          </div>

          <div class="integrations">
            <span class="int-label">Integrado com</span>
            <div class="int-chips">
              {#each ['Localiza', 'Movida', 'Unidas', '+5 redes'] as brand}
                <span class="int-chip">{brand}</span>
              {/each}
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</section>

<!-- COMO FUNCIONA -->
<section id="como-funciona" class="section" class:visible={sectionsVisible['how']} data-section="how">
  <div class="section-inner">
    <p class="section-label">Como funciona</p>
    <h2>Simples para você,<br /><em>poderoso para o mercado</em></h2>
    <div class="steps">
      {#each [
        { num: '01', title: 'Cadastre sua locadora', desc: 'Crie sua conta, adicione seus veículos com fotos, categorias, preços e disponibilidade em um painel intuitivo.' },
        { num: '02', title: 'Conectamos às grandes redes', desc: 'Traduzimos automaticamente seus dados para a API de cada grande locadora parceira. Zero trabalho técnico.' },
        { num: '03', title: 'Receba reservas e gerencie', desc: 'As reservas chegam centralizadas no seu painel. Você aprova, gerencia e acompanha tudo em tempo real.' }
      ] as step, i}
        <div class="step" style="transition-delay: {i * 0.12}s">
          <div class="step-num">{step.num}</div>
          <div class="step-line"></div>
          <h3>{step.title}</h3>
          <p>{step.desc}</p>
        </div>
      {/each}
    </div>
  </div>
</section>

<!-- PARA QUEM -->
<section id="para-quem" class="section" class:visible={sectionsVisible['audience']} data-section="audience">
  <div class="section-inner">
    <p class="section-label">Para quem é</p>
    <h2>Feito para locadoras<br /><em>que querem crescer</em></h2>
    <div class="cards">
      {#each [
        { icon: '◈', title: 'Pequenas locadoras', desc: 'Você tem a frota. Nós temos os clientes. Chegue a reservas que antes só as grandes tinham acesso.', items: ['Painel de gestão completo', 'Relatórios financeiros', 'Suporte dedicado'] },
        { icon: '◎', title: 'Locadoras em crescimento', desc: 'Expanda seu alcance sem expandir sua equipe. Nossa API cuida de todas as integrações automaticamente.', items: ['API padronizada', 'Múltiplas integrações', 'Dashboard em tempo real'] },
        { icon: '◇', title: 'Frotas corporativas', desc: 'Gerencie e alugue sua frota ociosa. Transforme custo em receita com facilidade.', items: ['Gestão de frota completa', 'Contratos flexíveis', 'Faturamento automático'] }
      ] as card, i}
        <div class="card" style="transition-delay: {i * 0.1}s">
          <span class="card-icon">{card.icon}</span>
          <h3>{card.title}</h3>
          <p>{card.desc}</p>
          <ul>
            {#each card.items as item}
              <li>
                <svg width="14" height="14" viewBox="0 0 14 14" fill="none"><path d="M2 7l3.5 3.5L12 3" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/></svg>
                {item}
              </li>
            {/each}
          </ul>
        </div>
      {/each}
    </div>
  </div>
</section>

<!-- CTA BAND -->
<div class="cta-band" class:visible={sectionsVisible['band']} data-section="band">
  <div class="band-inner">
    <div>
      <h2>Pronto para conectar<br /><em>sua frota ao Brasil?</em></h2>
      <p>Cadastro gratuito. Sem taxa de setup. Comece a receber reservas em até 48h.</p>
    </div>
    <div class="band-actions">
      <a href="/locadora/cadastro" class="cta-main">Cadastrar minha locadora</a>
      <a href="#contato" class="cta-outline">Falar com a equipe</a>
    </div>
  </div>
</div>

<!-- CONTATO -->
<section id="contato" class="section" class:visible={sectionsVisible['contact']} data-section="contact">
  <div class="section-inner contact-grid">
    <div class="contact-left">
      <p class="section-label">Contato</p>
      <h2>Tem dúvidas?<br /><em>A gente responde</em></h2>
      <p class="contact-sub">Nossa equipe está pronta para ajudar sua locadora a dar o próximo passo.</p>
      <div class="contact-info">
        <div class="contact-item"><span>✉</span><span>contato@carrental.com.br</span></div>
        <div class="contact-item"><span>🕐</span><span>Seg–Sex, 9h–18h</span></div>
      </div>
    </div>
    <form class="contact-form" onsubmit={(e) => e.preventDefault()}>
      <div class="form-row">
        <div class="form-group">
          <label for="nome">Nome</label>
          <input id="nome" type="text" placeholder="Seu nome" />
        </div>
        <div class="form-group">
          <label for="email">E-mail</label>
          <input id="email" type="email" placeholder="seu@email.com" />
        </div>
      </div>
      <div class="form-group">
        <label for="empresa">Nome da locadora</label>
        <input id="empresa" type="text" placeholder="Nome da sua empresa" />
      </div>
      <div class="form-group">
        <label for="msg">Mensagem</label>
        <textarea id="msg" rows="4" placeholder="Como podemos ajudar?"></textarea>
      </div>
      <button type="submit" class="cta-main full">Enviar mensagem</button>
    </form>
  </div>
</section>

<!-- FOOTER -->
<footer>
  <div class="footer-inner">
    <div class="footer-brand">
      <a href="/" class="logo"><span class="logo-icon">◈</span> CarRental</a>
      <p>A ponte entre pequenas locadoras e o mercado nacional de aluguel de veículos.</p>
    </div>
    <div class="footer-links">
      <div class="fl-col">
        <span>Produto</span>
        <a href="#como-funciona">Como funciona</a>
        <a href="#para-quem">Para quem</a>
        <a href="/locadora/cadastro">Cadastrar</a>
      </div>
      <div class="fl-col">
        <span>Acesso</span>
        <a href="/locadora/login">Login — Locadora</a>
        <a href="/superadmin/login">Login — Admin</a>
        <a href="/docs">Documentação API</a>
      </div>
      <div class="fl-col">
        <span>Legal</span>
        <a href="/privacidade">Privacidade</a>
        <a href="/termos">Termos de uso</a>
      </div>
    </div>
  </div>
  <div class="footer-bottom">
    <span>© 2025 CarRental Marketplace. Todos os direitos reservados.</span>
  </div>
</footer>