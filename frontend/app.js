// Configuration de l'API
const API_BASE_URL = 'http://localhost:8001';

// État de l'application
const state = {
    agents: [],
    currentDebate: null,
    selectedAgent1: null,
    selectedAgent2: null
};

// Éléments DOM
const elements = {
    agent1Select: document.getElementById('agent1-select'),
    agent2Select: document.getElementById('agent2-select'),
    agent1Info: document.getElementById('agent1-info'),
    agent2Info: document.getElementById('agent2-info'),
    createAgentBtn: document.getElementById('create-agent-btn'),
    startDebateBtn: document.getElementById('start-debate-btn'),
    nextTurnBtn: document.getElementById('next-turn-btn'),
    stopDebateBtn: document.getElementById('stop-debate-btn'),
    debateTopic: document.getElementById('debate-topic'),
    maxTurns: document.getElementById('max-turns'),
    openingStatements: document.getElementById('opening-statements'),
    closingStatements: document.getElementById('closing-statements'),
    debateArena: document.getElementById('debate-arena'),
    debateMessages: document.getElementById('debate-messages'),
    debateInfo: document.getElementById('debate-info'),
    agentModal: document.getElementById('agent-modal'),
    agentForm: document.getElementById('agent-form'),
    closeModal: document.querySelector('.close')
};

// ===== API Calls =====

async function fetchAgents() {
    try {
        const response = await fetch(`${API_BASE_URL}/agents`);
        if (!response.ok) throw new Error('Erreur lors du chargement des agents');
        state.agents = await response.json();
        updateAgentSelects();
    } catch (error) {
        console.error('Erreur:', error);
        showError('Impossible de charger les agents. Vérifiez que le serveur est démarré.');
    }
}

async function createAgent(agentData) {
    try {
        const response = await fetch(`${API_BASE_URL}/agents`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(agentData)
        });
        if (!response.ok) throw new Error('Erreur lors de la création de l\'agent');
        const agent = await response.json();
        state.agents.push(agent);
        updateAgentSelects();
        return agent;
    } catch (error) {
        console.error('Erreur:', error);
        showError('Impossible de créer l\'agent.');
        throw error;
    }
}

async function createDebate(debateData) {
    try {
        const response = await fetch(`${API_BASE_URL}/debates`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(debateData)
        });
        if (!response.ok) throw new Error('Erreur lors de la création du débat');
        state.currentDebate = await response.json();
        return state.currentDebate;
    } catch (error) {
        console.error('Erreur:', error);
        showError('Impossible de créer le débat.');
        throw error;
    }
}

// ===== UI Updates =====

function updateAgentSelects() {
    const options = state.agents.map(agent => 
        `<option value="${agent.id}">${agent.name} (${agent.debate_style})</option>`
    ).join('');
    
    elements.agent1Select.innerHTML = '<option value="">Sélectionner un agent...</option>' + options;
    elements.agent2Select.innerHTML = '<option value="">Sélectionner un agent...</option>' + options;
}

function displayAgentInfo(agent, infoElement) {
    if (!agent) {
        infoElement.innerHTML = '';
        return;
    }
    
    infoElement.innerHTML = `
        <p><strong>Modèle:</strong> ${agent.model} (${agent.ai_provider})</p>
        <p><strong>Style:</strong> ${agent.debate_style}</p>
        <p><strong>Ton:</strong> ${agent.tone}</p>
        <p><strong>Stratégie:</strong> ${agent.argumentation_strategy}</p>
        <p><strong>Description:</strong> ${agent.description}</p>
    `;
}

function showDebateArena() {
    document.getElementById('agent-selection').style.display = 'none';
    document.getElementById('debate-config').style.display = 'none';
    elements.debateArena.classList.remove('hidden');
}

function hideDebateArena() {
    document.getElementById('agent-selection').style.display = 'block';
    document.getElementById('debate-config').style.display = 'block';
    elements.debateArena.classList.add('hidden');
    elements.debateMessages.innerHTML = '';
}

function displayDebateInfo() {
    if (!state.currentDebate) return;
    
    const agent1 = state.agents.find(a => a.id === state.currentDebate.agent1_id);
    const agent2 = state.agents.find(a => a.id === state.currentDebate.agent2_id);
    
    elements.debateInfo.innerHTML = `
        <h3>📋 ${state.currentDebate.topic}</h3>
        <p><strong>Agent 1:</strong> ${agent1?.name} vs <strong>Agent 2:</strong> ${agent2?.name}</p>
        <p><strong>Tour:</strong> ${state.currentDebate.current_turn} / ${state.currentDebate.config.max_turns}</p>
        <p><strong>Statut:</strong> ${state.currentDebate.status}</p>
    `;
}

function addMessageToDebate(message, agentClass, agentName) {
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${agentClass}`;
    messageDiv.innerHTML = `
        <div class="message-header">
            <span>${agentName}</span>
            <span>Tour ${message.turn_number}</span>
        </div>
        <div class="message-content">${message.content}</div>
    `;
    elements.debateMessages.appendChild(messageDiv);
    elements.debateMessages.scrollTop = elements.debateMessages.scrollHeight;
}

function showError(message) {
    alert('❌ ' + message);
}

function showSuccess(message) {
    alert('✅ ' + message);
}

// ===== Event Handlers =====

elements.agent1Select.addEventListener('change', (e) => {
    state.selectedAgent1 = state.agents.find(a => a.id === e.target.value);
    displayAgentInfo(state.selectedAgent1, elements.agent1Info);
});

elements.agent2Select.addEventListener('change', (e) => {
    state.selectedAgent2 = state.agents.find(a => a.id === e.target.value);
    displayAgentInfo(state.selectedAgent2, elements.agent2Info);
});

elements.createAgentBtn.addEventListener('click', () => {
    elements.agentModal.classList.remove('hidden');
    elements.agentModal.classList.add('show');
});

elements.closeModal.addEventListener('click', () => {
    elements.agentModal.classList.remove('show');
    elements.agentModal.classList.add('hidden');
});

elements.agentForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    
    const agentData = {
        name: document.getElementById('agent-name').value,
        ai_provider: document.getElementById('agent-provider').value,
        model: document.getElementById('agent-model').value,
        description: document.getElementById('agent-description').value,
        debate_style: document.getElementById('agent-style').value,
        tone: document.getElementById('agent-tone').value,
        argumentation_strategy: document.getElementById('agent-strategy').value,
        personality_traits: [],
        expertise_domains: []
    };
    
    try {
        await createAgent(agentData);
        elements.agentModal.classList.remove('show');
        elements.agentModal.classList.add('hidden');
        elements.agentForm.reset();
        showSuccess('Agent créé avec succès!');
    } catch (error) {
        // Erreur déjà gérée dans createAgent
    }
});

elements.startDebateBtn.addEventListener('click', async () => {
    if (!state.selectedAgent1 || !state.selectedAgent2) {
        showError('Veuillez sélectionner deux agents.');
        return;
    }
    
    if (state.selectedAgent1.id === state.selectedAgent2.id) {
        showError('Les deux agents doivent être différents.');
        return;
    }
    
    const topic = elements.debateTopic.value.trim();
    if (!topic) {
        showError('Veuillez entrer un sujet de débat.');
        return;
    }
    
    const debateData = {
        topic: topic,
        agent1_id: state.selectedAgent1.id,
        agent2_id: state.selectedAgent2.id,
        config: {
            topic: topic,
            max_turns: parseInt(elements.maxTurns.value),
            opening_statement_required: elements.openingStatements.checked,
            closing_statement_required: elements.closingStatements.checked,
            allow_questions: true,
            moderated: false
        },
        status: "in_progress",
        messages: []
    };
    
    try {
        await createDebate(debateData);
        showDebateArena();
        displayDebateInfo();
        showSuccess('Débat créé! Cliquez sur "Tour suivant" pour commencer.');
    } catch (error) {
        // Erreur déjà gérée dans createDebate
    }
});

elements.nextTurnBtn.addEventListener('click', async () => {
    if (!state.currentDebate) return;
    
    elements.nextTurnBtn.disabled = true;
    elements.nextTurnBtn.textContent = 'Génération en cours...';
    
    try {
        const response = await fetch(`${API_BASE_URL}/debates/${state.currentDebate.id}/next-turn`, {
            method: 'POST'
        });
        
        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || 'Erreur lors de la génération');
        }
        
        const data = await response.json();
        
        // Mettre à jour le débat local
        state.currentDebate = data.debate;
        
        // Afficher le nouveau message
        const agent = state.agents.find(a => a.id === data.message.agent_id);
        const agentClass = data.message.role === 'agent1' ? 'agent1' : 'agent2';
        const agentName = agent ? agent.name : data.message.role;
        
        addMessageToDebate(data.message, agentClass, agentName);
        displayDebateInfo();
        
        // Vérifier si le débat est terminé
        if (state.currentDebate.status === 'completed') {
            elements.nextTurnBtn.disabled = true;
            elements.nextTurnBtn.textContent = 'Débat terminé';
            showSuccess('Le débat est terminé !');
        } else {
            elements.nextTurnBtn.disabled = false;
            elements.nextTurnBtn.textContent = 'Tour suivant';
        }
        
    } catch (error) {
        console.error('Erreur:', error);
        showError(error.message);
        elements.nextTurnBtn.disabled = false;
        elements.nextTurnBtn.textContent = 'Tour suivant';
    }
});

elements.stopDebateBtn.addEventListener('click', () => {
    if (confirm('Voulez-vous vraiment arrêter le débat?')) {
        hideDebateArena();
        state.currentDebate = null;
    }
});

// Fermer le modal en cliquant en dehors
window.addEventListener('click', (e) => {
    if (e.target === elements.agentModal) {
        elements.agentModal.classList.remove('show');
        elements.agentModal.classList.add('hidden');
    }
});

// ===== Initialisation =====

async function init() {
    console.log('🚀 Initialisation de l\'application AI Debate...');
    await fetchAgents();
    console.log('✅ Application prête!');
}

// Démarrer l'application
init();
