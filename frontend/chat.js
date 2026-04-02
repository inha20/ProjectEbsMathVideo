/**
 * Chat UI Module
 * Handles chat message display, input, and AI interaction.
 */

let chatInitialized = false;

// ──────────────────────────────────────────────
// Init Chat
// ──────────────────────────────────────────────
async function initChat() {
    if (chatInitialized) return;
    chatInitialized = true;

    const input = document.getElementById('chat-input');
    const sendBtn = document.getElementById('chat-send');

    // Send on button click
    sendBtn.addEventListener('click', () => sendMessage());

    // Send on Enter
    input.addEventListener('keydown', (e) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            sendMessage();
        }
    });

    // Quick action buttons
    document.querySelectorAll('.quick-btn').forEach(btn => {
        btn.addEventListener('click', () => {
            const msg = btn.dataset.msg;
            document.getElementById('chat-input').value = msg;
            sendMessage();
        });
    });

    // Start chat session
    await startChatSession();
}

// ──────────────────────────────────────────────
// Start Session
// ──────────────────────────────────────────────
async function startChatSession() {
    try {
        const data = await apiPost('/chat/start');
        AppState.sessionId = data.session_id;
        appendMessage('assistant', data.message);
    } catch (err) {
        appendMessage('assistant', 
            '안녕하세요! 🎓 수학 영상 추천 도우미입니다.\n\n' +
            '⚠️ 서버에 연결할 수 없어요. 백엔드 서버가 실행 중인지 확인해주세요.\n\n' +
            '`python main.py` 로 서버를 시작해주세요!'
        );
    }
}

// ──────────────────────────────────────────────
// Send Message
// ──────────────────────────────────────────────
async function sendMessage() {
    const input = document.getElementById('chat-input');
    const msg = input.value.trim();
    if (!msg) return;

    // Show user message
    appendMessage('user', msg);
    input.value = '';
    input.focus();

    // Show typing indicator
    showTyping();

    try {
        const data = await apiPost('/chat/message', {
            session_id: AppState.sessionId,
            message: msg,
        });

        hideTyping();
        appendMessage('assistant', data.message);

        // Handle recommendations
        if (data.recommendations && data.search_keywords) {
            handleRecommendations(data);
        }

        // Update quick actions based on state
        updateQuickActions(data.state);

    } catch (err) {
        hideTyping();
        appendMessage('assistant', 
            '죄송해요, 응답을 받지 못했어요. 😅\n서버 연결을 확인해주세요.'
        );
    }
}

// ──────────────────────────────────────────────
// Message Rendering
// ──────────────────────────────────────────────
function appendMessage(role, text) {
    const container = document.getElementById('chat-messages');

    const msgEl = document.createElement('div');
    msgEl.className = `msg ${role}`;

    // Simple markdown-like formatting
    let html = text
        .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
        .replace(/\n/g, '<br>')
        .replace(/• /g, '&bull; ');

    const now = new Date();
    const timeStr = `${now.getHours().toString().padStart(2, '0')}:${now.getMinutes().toString().padStart(2, '0')}`;

    msgEl.innerHTML = `${html}<span class="msg-time">${timeStr}</span>`;
    container.appendChild(msgEl);

    // Auto-scroll to bottom
    container.scrollTop = container.scrollHeight;
}

function showTyping() {
    const container = document.getElementById('chat-messages');
    const typing = document.createElement('div');
    typing.className = 'typing-indicator';
    typing.id = 'typing-indicator';
    typing.innerHTML = `
        <span class="typing-dot"></span>
        <span class="typing-dot"></span>
        <span class="typing-dot"></span>
    `;
    container.appendChild(typing);
    container.scrollTop = container.scrollHeight;
}

function hideTyping() {
    const el = document.getElementById('typing-indicator');
    if (el) el.remove();
}

// ──────────────────────────────────────────────
// Handle Recommendations
// ──────────────────────────────────────────────
async function handleRecommendations(data) {
    const keywords = data.search_keywords;
    const rec = data.recommendations;

    // Auto-search YouTube with first keyword
    if (keywords && keywords.length > 0 && typeof searchYouTube === 'function') {
        await searchYouTube(keywords[0]);
    }

    // Load EBS recommendations
    if (data.ebs_courses && data.ebs_courses.length > 0 && typeof renderEBSResults === 'function') {
        renderEBSResults(data.ebs_courses);
    }

    // Add notification about results
    setTimeout(() => {
        appendMessage('assistant', 
            '🎯 추천 결과가 준비되었어요!\n\n' +
            '• **YouTube** 탭에서 영상을 확인하세요 ▶️\n' +
            '• **EBS 강좌** 탭에서 EBS 추천을 확인하세요 📚\n' +
            '• 마음에 드는 영상은 **재생목록**에 추가해보세요!'
        );
    }, 500);
}

// ──────────────────────────────────────────────
// Dynamic Quick Actions
// ──────────────────────────────────────────────
function updateQuickActions(state) {
    const container = document.getElementById('quick-actions');
    if (!state) return;

    if (state.state === 'ask_topic') {
        const level = state.level;
        const topicMap = {
            middle: ['일차방정식', '이차함수', '인수분해', '피타고라스'],
            high: ['수학I', '수학II', '미적분', '확률과 통계'],
            suneung: ['수능특강', '미적분', '확률과 통계', '기하'],
        };
        const topics = topicMap[level] || topicMap.high;
        container.innerHTML = topics.map(t => 
            `<button class="quick-btn" data-msg="${t}">${t}</button>`
        ).join('');
    } else if (state.state === 'ask_difficulty') {
        container.innerHTML = `
            <button class="quick-btn" data-msg="기초부터 배우고 싶어요">🌱 기초</button>
            <button class="quick-btn" data-msg="중간 정도">🌿 중급</button>
            <button class="quick-btn" data-msg="심화 문제 풀고 싶어요">🌳 심화</button>
        `;
    } else if (state.state === 'recommend') {
        container.innerHTML = `
            <button class="quick-btn" data-msg="다른 주제도 검색해줘">🔄 다른 주제</button>
            <button class="quick-btn" data-msg="수능 준비하고 있어요">📝 수능 전환</button>
        `;
    }

    // Rebind quick action events
    container.querySelectorAll('.quick-btn').forEach(btn => {
        btn.addEventListener('click', () => {
            document.getElementById('chat-input').value = btn.dataset.msg;
            sendMessage();
        });
    });
}
