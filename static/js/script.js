document.addEventListener('DOMContentLoaded', function() {
    // Configuração do carrossel de depoimentos
    if (document.querySelector('.glide')) {
        new Glide('.glide', {
            type: 'carousel',
            perView: 1,
            gap: 30,
            autoplay: 5000,
            hoverpause: true
        }).mount();
    }

    // Controle da tela de etapas
    const abrirBtn = document.querySelector('.abrir-etapas-btn');
    const fecharBtn = document.querySelector('.fechar-etapas');
    const etapasFlutuante = document.querySelector('.etapas-flutuante');
    const etapaBtns = document.querySelectorAll('.etapa-btn');
    
    if (abrirBtn && etapasFlutuante) {
        abrirBtn.addEventListener('click', () => {
            etapasFlutuante.classList.add('mostrar');
        });
        
        fecharBtn.addEventListener('click', () => {
            etapasFlutuante.classList.remove('mostrar');
        });
        
        etapaBtns.forEach(btn => {
            btn.addEventListener('click', () => {
                // Remove active de todos
                document.querySelectorAll('.etapa-btn.active').forEach(el => el.classList.remove('active'));
                document.querySelectorAll('.etapa-conteudo.active').forEach(el => el.classList.remove('active'));
                
                // Adiciona active no selecionado
                btn.classList.add('active');
                const etapa = btn.dataset.etapa;
                document.querySelector(`.etapa-conteudo[data-etapa="${etapa}"]`).classList.add('active');
            });
        });
        
        // Fechar ao clicar fora
        etapasFlutuante.addEventListener('click', (e) => {
            if (e.target === etapasFlutuante) {
                etapasFlutuante.classList.remove('mostrar');
            }
        });
    }

    // Cards expansíveis
    const expandableCards = document.querySelectorAll('.expandable-card');
    
    expandableCards.forEach(card => {
        const header = card.querySelector('.card-header');
        const content = card.querySelector('.card-content');
        const icon = card.querySelector('.expand-icon');
        
        header.addEventListener('click', () => {
            card.classList.toggle('active');
            
            if (card.classList.contains('active')) {
                content.style.maxHeight = content.scrollHeight + 'px';
            } else {
                content.style.maxHeight = '0';
            }
        });
    });

    // Smooth scrolling para links de navegação
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function(e) {
            e.preventDefault();
            
            const targetId = this.getAttribute('href');
            const targetElement = document.querySelector(targetId);
            
            if (targetElement) {
                window.scrollTo({
                    top: targetElement.offsetTop - 80, // Ajuste para a navbar fixa
                    behavior: 'smooth'
                });
            }
        });
    });
});

// Função para alternar a tela flutuante
function toggleEtapasFlutuante() {
    const flutuante = document.querySelector('.etapas-flutuante');
    flutuante.classList.toggle('ativo');
    
    // Opcional: desabilita scroll da página quando a tela está aberta
    document.body.style.overflow = flutuante.classList.contains('ativo') ? 'hidden' : '';
}

// Inicialização dos eventos
document.addEventListener('DOMContentLoaded', function() {
    // Verifica se os elementos existem
    const abrirBtn = document.querySelector('.abrir-etapas-btn');
    const fecharBtn = document.querySelector('.fechar-etapas');
    
    if (!abrirBtn || !fecharBtn) {
        console.error('Elementos não encontrados!');
        return;
    }
    
    // Adiciona eventos
    abrirBtn.addEventListener('click', toggleEtapasFlutuante);
    fecharBtn.addEventListener('click', toggleEtapasFlutuante);
    
    // Navegação entre etapas
    document.querySelectorAll('.etapa-btn').forEach(btn => {
        btn.addEventListener('click', function() {
            // Remove classe active de todos os botões
            document.querySelectorAll('.etapa-btn').forEach(b => b.classList.remove('active'));
            // Adiciona classe active ao botão clicado
            this.classList.add('active');
            
            // Esconde todos os conteúdos
            document.querySelectorAll('.etapa-conteudo').forEach(content => {
                content.classList.remove('active');
            });
            
            // Mostra o conteúdo correspondente
            const etapa = this.getAttribute('data-etapa');
            document.querySelector(`.etapa-conteudo[data-etapa="${etapa}"]`).classList.add('active');
        });
    });
    
    // Garante que o botão está visível
    abrirBtn.style.display = 'flex';
});