// Configuration de l'API
const API_BASE_URL = 'https://ai-debate-api-66nr2u3stq-uk.a.run.app';

// État de l'application
const state = {
    agents: [],
    preconfiguredDebates: [],
    currentDebate: null,
    selectedAgent1: null,
    selectedAgent2: null,
    selectedPreconfiguredDebate: null
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
    preconfiguredDebatesSelect: document.getElementById('preconfigured-debates'),
    responseLengthSelect: document.getElementById('response-length'),
    debateDetails: document.getElementById('debate-details'),
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

async function fetchPreconfiguredDebates() {
    try {
        const response = await fetch(`${API_BASE_URL}/debates`);
        if (!response.ok) throw new Error('Erreur lors du chargement des débats');
        const data = await response.json();
        state.preconfiguredDebates = data.debates || [];
        //display debates
        //display json data in console for debugging
        console.log('Débats préconfigurés chargés:', state.preconfiguredDebates);
        updatePreconfiguredDebatesSelect();
    } catch (error) {
        console.error('Erreur:', error);
        showError('Impossible de charger les débats préconfigurés.');
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

function updatePreconfiguredDebatesSelect() {
    const options = state.preconfiguredDebates
        .filter(debate => debate.status === 'pending')
        .map(debate => 
            `<option value="${debate.id}">${debate.topic}</option>`
        ).join('');
    //display debates
    elements.preconfiguredDebatesSelect.innerHTML = '<option value="">Sélectionner un débat...</option>' + options;
}

function displayDebateDetails(debate) {
    if (!debate) {
        elements.debateDetails.classList.add('hidden');
        return;
    }
    
    const agent1 = state.agents.find(a => a.id === debate.agent1_id);
    const agent2 = state.agents.find(a => a.id === debate.agent2_id);
    
    const responseLength = elements.responseLengthSelect.value || 'moyen';
    
    document.getElementById('selected-topic').textContent = debate.topic;
    document.getElementById('selected-agent1').textContent = agent1?.name || debate.agent1_id;
    document.getElementById('selected-agent2').textContent = agent2?.name || debate.agent2_id;
    document.getElementById('selected-pos1').textContent = debate.config?.agent1_position || 'pour';
    document.getElementById('selected-pos2').textContent = debate.config?.agent2_position || 'contre';
    document.getElementById('selected-turns').textContent = debate.config?.max_turns || 10;
    document.getElementById('selected-length').textContent = responseLength.charAt(0).toUpperCase() + responseLength.slice(1);
    
    elements.debateDetails.classList.remove('hidden');
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
    // Récupérer et formater les positions (pour/contre/neutre)
    const pos1 = state.currentDebate.config && state.currentDebate.config.agent1_position ? state.currentDebate.config.agent1_position : null;
    const pos2 = state.currentDebate.config && state.currentDebate.config.agent2_position ? state.currentDebate.config.agent2_position : null;
    function humanizePos(p) {
        if (!p) return 'Neutre';
        if (p.toLowerCase() === 'pour') return 'Pour';
        if (p.toLowerCase() === 'contre') return 'Contre';
        return p.charAt(0).toUpperCase() + p.slice(1);
    }

    elements.debateInfo.innerHTML = `
        <h3>📋 ${state.currentDebate.topic}</h3>
        <p><strong>Agent 1:</strong> ${agent1?.name} <strong>(${humanizePos(pos1)})</strong> vs <strong>Agent 2:</strong> ${agent2?.name} <strong>(${humanizePos(pos2)})</strong></p>
        <p><strong>Tour:</strong> ${state.currentDebate.current_turn+1} / ${state.currentDebate.config.max_turns}</p>
        <p><strong>Statut:</strong> ${state.currentDebate.status}</p>
    `;
}

function addMessageToDebate(message, agentClass, agentName) {
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${agentClass}`;
    messageDiv.innerHTML = `
        <div class="message-header">
            <span>${agentName}</span>
            <span>Tour ${message.turn_number + 1}</span>
        </div>
        <div class="message-content">${message.content}</div>
    `;
    elements.debateMessages.appendChild(messageDiv);
    elements.debateMessages.scrollTop = elements.debateMessages.scrollHeight;
}

function showError(message) {
    if (window.Swal) {
        Swal.fire({
            icon: 'error',
            title: 'Erreur',
            text: message
        });
    } else {
        alert('❌ ' + message);
    }
}

function showSuccess(message) {
    if (window.Swal) {
        Swal.fire({
            icon: 'success',
            title: 'Succès',
            text: message,
            timer: 1400,
            showConfirmButton: false
        });
    } else {
        alert('✅ ' + message);
    }
}

// Spinner helpers shown while backend prépare le débat (crawl / start)
function showSpinner() {
    const el = document.getElementById('spinner-overlay');
    if (el) el.classList.remove('hidden');
}

function hideSpinner() {
    const el = document.getElementById('spinner-overlay');
    if (el) el.classList.add('hidden');
}

// ===== Event Handlers =====

elements.agent1Select.addEventListener('change', (e) => {
    state.selectedAgent1 = state.agents.find(a => a.id === e.target.value);
    displayAgentInfo(state.selectedAgent1, elements.agent1Info);
    
    // Mettre à jour le débat préconfiguré sélectionné avec le nouvel agent
    if (state.selectedPreconfiguredDebate && state.selectedAgent1) {
        state.selectedPreconfiguredDebate.agent1_id = state.selectedAgent1.id;
        displayDebateDetails(state.selectedPreconfiguredDebate);
    }
});

elements.agent2Select.addEventListener('change', (e) => {
    state.selectedAgent2 = state.agents.find(a => a.id === e.target.value);
    displayAgentInfo(state.selectedAgent2, elements.agent2Info);
    
    // Mettre à jour le débat préconfiguré sélectionné avec le nouvel agent
    if (state.selectedPreconfiguredDebate && state.selectedAgent2) {
        state.selectedPreconfiguredDebate.agent2_id = state.selectedAgent2.id;
        displayDebateDetails(state.selectedPreconfiguredDebate);
    }
});

elements.preconfiguredDebatesSelect.addEventListener('change', (e) => {
    const debateId = e.target.value;
    state.selectedPreconfiguredDebate = state.preconfiguredDebates.find(d => d.id === debateId);
    
    // Mettre à jour automatiquement les agents sélectionnés si le débat en a
    if (state.selectedPreconfiguredDebate) {
        if (state.selectedPreconfiguredDebate.agent1_id) {
            elements.agent1Select.value = state.selectedPreconfiguredDebate.agent1_id;
            state.selectedAgent1 = state.agents.find(a => a.id === state.selectedPreconfiguredDebate.agent1_id);
            displayAgentInfo(state.selectedAgent1, elements.agent1Info);
        }
        
        if (state.selectedPreconfiguredDebate.agent2_id) {
            elements.agent2Select.value = state.selectedPreconfiguredDebate.agent2_id;
            state.selectedAgent2 = state.agents.find(a => a.id === state.selectedPreconfiguredDebate.agent2_id);
            displayAgentInfo(state.selectedAgent2, elements.agent2Info);
        }
        
        // Mettre à jour la longueur des réponses selon la config du débat
        if (state.selectedPreconfiguredDebate.config?.response_length) {
            elements.responseLengthSelect.value = state.selectedPreconfiguredDebate.config.response_length;
        }
    }
    
    displayDebateDetails(state.selectedPreconfiguredDebate);
});

elements.responseLengthSelect.addEventListener('change', () => {
    if (state.selectedPreconfiguredDebate) {
        displayDebateDetails(state.selectedPreconfiguredDebate);
    }
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
    if (!state.selectedPreconfiguredDebate) {
        showError('Veuillez sélectionner un débat préconfiguré.');
        return;
    }
    
    if (!state.selectedAgent1 || !state.selectedAgent2) {
        showError('Les agents ne sont pas correctement sélectionnés.');
        return;
    }
    
    try {
        // Préparer la configuration du débat avec les agents sélectionnés
        const responseLength = elements.responseLengthSelect.value || 'moyen';
        
        const debateConfig = {
            topic: state.selectedPreconfiguredDebate.topic,
            agent1_id: state.selectedAgent1.id,
            agent2_id: state.selectedAgent2.id,
            config: {
                agent1_position: state.selectedPreconfiguredDebate.config?.agent1_position || 'pour',
                agent2_position: state.selectedPreconfiguredDebate.config?.agent2_position || 'contre',
                max_turns: state.selectedPreconfiguredDebate.config?.max_turns || 10,
                source_url: state.selectedPreconfiguredDebate.config?.source_url || null,
                response_length: responseLength
            }
        };
        
        // Créer le débat côté serveur avec la configuration complète
        state.currentDebate = await createDebate(debateConfig);
        
        if (!state.currentDebate) {
            showError('Échec de la création du débat.');
            return;
        }
        
        // Appeler l'endpoint de démarrage pour que le backend puisse préparer le débat
        let started = true;
        try {
            // Afficher le spinner pendant que le backend prépare la source
            showSpinner();
            try {
                const startResp = await fetch(`${API_BASE_URL}/debates/${state.currentDebate.id}/start`, {
                    method: 'POST'
                });
                if (startResp.ok) {
                    const startData = await startResp.json();
                    // backend retourne { success: True, debate: debate }
                    if (startData.debate) {
                        state.currentDebate = startData.debate;
                    }
                } else {
                    const text = await startResp.text();
                    try {
                        const err = JSON.parse(text);
                        showError(err.detail || 'Erreur au démarrage du débat');
                    } catch (e) {
                        showError(text || 'Erreur au démarrage du débat');
                    }
                    started = false;
                }
            } catch (e) {
                showError('Impossible de joindre le serveur pour démarrer le débat.');
                started = false;
            } finally {
                hideSpinner();
            }
        } catch (error) {
            // ne devrait pas arriver mais on s'assure de masquer le spinner
            hideSpinner();
            throw error;
        }

        if (!started) return;

        showDebateArena();
        displayDebateInfo();
    } catch (error) {
        // Erreur déjà gérée dans createDebate
    }
});

elements.nextTurnBtn.addEventListener('click', async () => {
    if (!state.currentDebate) return;
    
    elements.nextTurnBtn.disabled = true;
    elements.nextTurnBtn.textContent = 'Génération en cours...';
    
    try {
        // Utiliser fetch + ReadableStream pour consommer le flux SSE renvoyé par le serveur
        const resp = await fetch(`${API_BASE_URL}/debates/${state.currentDebate.id}/next-turn/stream`, {
            method: 'POST'
        });

        if (!resp.ok) {
            const err = await resp.json();
            throw new Error(err.detail || 'Erreur lors de la génération');
        }

        const reader = resp.body.getReader();
        const decoder = new TextDecoder();
        let buffer = '';

        // Préparer un message temporaire en UI
        const isAgent1Turn = (state.currentDebate.messages.length % 2) === 0;
        const currentAgent = isAgent1Turn ? state.agents.find(a => a.id === state.currentDebate.agent1_id) : state.agents.find(a => a.id === state.currentDebate.agent2_id);
        const agentClass = isAgent1Turn ? 'agent1' : 'agent2';
        const agentName = currentAgent ? currentAgent.name : (isAgent1Turn ? 'agent1' : 'agent2');

        // Placeholder DOM element
        const placeholderMsg = {
            content: '' ,
            turn_number: state.currentDebate.current_turn,
            agent_id: currentAgent ? currentAgent.id : null,
            role: isAgent1Turn ? 'agent1' : 'agent2'
        };

        // Afficher une ligne vide qui sera remplie au fil du streaming
        const placeholderDiv = document.createElement('div');
        placeholderDiv.className = `message ${agentClass}`;
        placeholderDiv.innerHTML = `
            <div class="message-header">
                <span>${agentName}</span>
                <span>Tour ${placeholderMsg.turn_number+1}</span>
            </div>
            <div class="message-content">...</div>
        `;
        elements.debateMessages.appendChild(placeholderDiv);
        elements.debateMessages.scrollTop = elements.debateMessages.scrollHeight;

        // Helper pour échapper le HTML
        function escapeHtml(unsafe) {
            return unsafe
                .replace(/&/g, "&amp;")
                .replace(/</g, "&lt;")
                .replace(/>/g, "&gt;")
                .replace(/"/g, "&quot;")
                .replace(/'/g, "&#039;");
        }

        // Lire le flux
        while (true) {
            const { value, done } = await reader.read();
            if (done) break;
            buffer += decoder.decode(value, { stream: true });

            // Les événements SSE sont séparés par double saut de ligne
            const parts = buffer.split('\n\n');
            buffer = parts.pop();

            for (const part of parts) {
                if (!part) continue;
                const lines = part.split('\n');
                for (const line of lines) {
                    if (!line.startsWith('data:')) continue;
                    const jsonText = line.replace(/^data:\s*/, '');
                    let payload = null;
                    try {
                        payload = JSON.parse(jsonText);
                    } catch (e) {
                        console.error('Erreur parsing payload streaming', e, jsonText);
                        continue;
                    }

                    if (payload.type === 'token') {
                        // Ajouter le segment au placeholder
                        placeholderMsg.content += payload.text;
                        let contentDiv = placeholderDiv.querySelector('.message-content');
                        if (!contentDiv) {
                            contentDiv = document.createElement('div');
                            contentDiv.className = 'message-content';
                            placeholderDiv.appendChild(contentDiv);
                        }
                        // Utiliser innerHTML en échappant pour préserver retours à la ligne
                        contentDiv.innerHTML = escapeHtml(placeholderMsg.content).replace(/\n/g, '<br>');
                        elements.debateMessages.scrollTop = elements.debateMessages.scrollHeight;
                    } else if (payload.type === 'done') {
                        // Finaliser le message
                        placeholderMsg.content = payload.message.content;
                        let contentDiv = placeholderDiv.querySelector('.message-content');
                        if (!contentDiv) {
                            contentDiv = document.createElement('div');
                            contentDiv.className = 'message-content';
                            placeholderDiv.appendChild(contentDiv);
                        }
                        contentDiv.innerHTML = escapeHtml(placeholderMsg.content).replace(/\n/g, '<br>');

                        // Récupérer l'état final du débat côté serveur pour mise à jour
                        try {
                            const finalResp = await fetch(`${API_BASE_URL}/debates/${state.currentDebate.id}`);
                            if (finalResp.ok) {
                                state.currentDebate = await finalResp.json();
                            }
                        } catch (e) {
                            console.warn('Impossible d\'obtenir le débat final:', e);
                        }

                        displayDebateInfo();

                        if (state.currentDebate.status === 'completed') {
                            showSuccess('Le débat est terminé !');
                            setTimeout(() => {
                                hideDebateArena();
                                state.currentDebate = null;
                            }, 1500);
                        } else {
                            elements.nextTurnBtn.disabled = false;
                            elements.nextTurnBtn.textContent = 'Tour suivant';
                        }
                    } else if (payload.type === 'error') {
                        throw new Error(payload.detail || 'Erreur streaming');
                    }
                }
            }
        }
        
    } catch (error) {
        console.error('Erreur:', error);
        showError(error.message);
        elements.nextTurnBtn.disabled = false;
        elements.nextTurnBtn.textContent = 'Tour suivant';
    }
});

elements.stopDebateBtn.addEventListener('click', async () => {
    if (window.Swal) {
        const res = await Swal.fire({
            title: 'Confirmer',
            text: 'Voulez-vous vraiment arrêter le débat?',
            icon: 'warning',
            showCancelButton: true,
            confirmButtonText: 'Oui',
            cancelButtonText: 'Annuler'
        });

        if (res.isConfirmed) {
            hideDebateArena();
            state.currentDebate = null;
        }
    } else {
        if (confirm('Voulez-vous vraiment arrêter le débat?')) {
            hideDebateArena();
            state.currentDebate = null;
        }
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
    await fetchPreconfiguredDebates();
    console.log('✅ Application prête!');
}

// Démarrer l'application
init();
