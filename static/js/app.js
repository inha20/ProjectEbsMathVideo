/**
 * app.js - 프론트엔드 애플리케이션 로직
 * EBS 수학 영상 학습 추천 시스템
 */

// ──────────────────────────────────────
// API 헬퍼
// ──────────────────────────────────────
const API = {
    async post(url, data) {
        const res = await fetch(url, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data),
        });
        return res.json();
    },
    async get(url) {
        const res = await fetch(url);
        return res.json();
    },
    async delete(url) {
        const res = await fetch(url, { method: 'DELETE' });
        return res.json();
    },
};

// ──────────────────────────────────────
// 상태 관리
// ──────────────────────────────────────
const state = {
    chatHistory: [],
    currentView: 'chat',
};

// ──────────────────────────────────────
// 네비게이션
// ──────────────────────────────────────
document.querySelectorAll('.nav-btn').forEach(btn => {
    btn.addEventListener('click', () => {
        const view = btn.dataset.view;
        switchView(view);
    });
});

function switchView(viewName) {
    // 버튼 활성화
    document.querySelectorAll('.nav-btn').forEach(b => b.classList.remove('active'));
    document.querySelector(`[data-view="${viewName}"]`).classList.add('active');

    // 뷰 전환
    document.querySelectorAll('.view').forEach(v => v.classList.remove('active'));
    document.getElementById(`view-${viewName}`).classList.add('active');

    state.currentView = viewName;

    // 뷰별 데이터 로드
    if (viewName === 'playlists') loadPlaylists();
    if (viewName === 'dashboard') loadDashboard();
}

// ──────────────────────────────────────
// 채팅 기능
// ──────────────────────────────────────
const chatInput = document.getElementById('chat-input');
const chatSendBtn = document.getElementById('chat-send-btn');
const chatMessages = document.getElementById('chat-messages');

chatSendBtn.addEventListener('click', sendMessage);
chatInput.addEventListener('keypress', e => {
    if (e.key === 'Enter') sendMessage();
});

async function sendMessage() {
    const message = chatInput.value.trim();
    if (!message) return;

    // 사용자 메시지 표시
    appendMessage('user', message);
    chatInput.value = '';
    chatInput.disabled = true;
    chatSendBtn.disabled = true;

    // 로딩 표시
    const loadingId = appendLoading();

    try {
        // API 호출
        const response = await API.post('/api/chat/', {
            message: message,
            history: state.chatHistory.slice(-10),
        });

        removeLoading(loadingId);

        // 봇 응답 표시
        appendBotMessage(response.reply, response.recommended_videos);

        // 대화 이력 업데이트
        state.chatHistory.push({ role: 'user', content: message });
        state.chatHistory.push({ role: 'assistant', content: response.reply });

    } catch (err) {
        removeLoading(loadingId);
        appendMessage('bot', '죄송합니다. 오류가 발생했습니다. 다시 시도해주세요.');
    }

    chatInput.disabled = false;
    chatSendBtn.disabled = false;
    chatInput.focus();
}

function appendMessage(role, content) {
    const div = document.createElement('div');
    div.className = `message ${role}`;

    const avatar = role === 'user' ? '👤' : '🤖';
    div.innerHTML = `
        <div class="message-avatar">${avatar}</div>
        <div class="message-content">
            <p>${escapeHtml(content)}</p>
        </div>
    `;

    chatMessages.appendChild(div);
    chatMessages.scrollTop = chatMessages.scrollHeight;
}

function appendBotMessage(reply, videos) {
    const div = document.createElement('div');
    div.className = 'message bot';

    // JSON 블록 제거 (AI 응답에서)
    let cleanReply = reply.replace(/```json[\s\S]*?```/g, '').trim();
    // 줄바꿈 → <br>
    cleanReply = cleanReply.replace(/\n/g, '<br>');
    // **bold** 처리
    cleanReply = cleanReply.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');

    let videosHtml = '';
    if (videos && videos.length > 0) {
        videosHtml = `
            <div class="recommended-videos">
                <p style="font-weight:600; margin-top:8px;">📺 추천 영상:</p>
                ${videos.map(v => `
                    <div class="rec-video-card" onclick="openVideo('${escapeAttr(v.url)}')">
                        <div class="rec-video-title">${escapeHtml(v.title)}</div>
                        <div class="rec-video-meta">
                            <span>${v.source === 'ebs' ? '📗 EBS' : '▶️ YouTube'}</span>
                            <span>${getDifficultyLabel(v.difficulty)}</span>
                        </div>
                        ${v.reason ? `<div class="rec-video-reason">💡 ${escapeHtml(v.reason)}</div>` : ''}
                    </div>
                `).join('')}
            </div>
        `;
    }

    div.innerHTML = `
        <div class="message-avatar">🤖</div>
        <div class="message-content">
            <p>${cleanReply}</p>
            ${videosHtml}
        </div>
    `;

    chatMessages.appendChild(div);
    chatMessages.scrollTop = chatMessages.scrollHeight;
}

function appendLoading() {
    const id = 'loading-' + Date.now();
    const div = document.createElement('div');
    div.className = 'message bot';
    div.id = id;
    div.innerHTML = `
        <div class="message-avatar">🤖</div>
        <div class="message-content">
            <span class="loading"></span> 생각 중...
        </div>
    `;
    chatMessages.appendChild(div);
    chatMessages.scrollTop = chatMessages.scrollHeight;
    return id;
}

function removeLoading(id) {
    const el = document.getElementById(id);
    if (el) el.remove();
}

// ──────────────────────────────────────
// 영상 검색
// ──────────────────────────────────────
document.getElementById('search-btn').addEventListener('click', searchVideos);
document.getElementById('search-query').addEventListener('keypress', e => {
    if (e.key === 'Enter') searchVideos();
});

async function searchVideos() {
    const query = document.getElementById('search-query').value.trim();
    if (!query) return;

    const grid = document.getElementById('search-results');
    grid.innerHTML = '<div class="empty-state"><span class="loading"></span><p>검색 중...</p></div>';

    try {
        const response = await API.post('/api/videos/search', {
            query: query,
            grade: document.getElementById('filter-grade').value || null,
            difficulty: document.getElementById('filter-difficulty').value || null,
            source: document.getElementById('filter-source').value || 'all',
            max_results: 12,
        });

        if (response.results && response.results.length > 0) {
            grid.innerHTML = response.results.map(v => createVideoCard(v)).join('');
        } else {
            grid.innerHTML = '<div class="empty-state"><span class="empty-icon">🔍</span><p>검색 결과가 없습니다</p></div>';
        }
    } catch (err) {
        grid.innerHTML = '<div class="empty-state"><span class="empty-icon">⚠️</span><p>검색 중 오류가 발생했습니다</p></div>';
    }
}

function createVideoCard(video) {
    const sourceClass = video.source === 'ebs' ? 'source-ebs' : 'source-youtube';
    const sourceLabel = video.source === 'ebs' ? 'EBS' : 'YouTube';
    const diffClass = `diff-${video.difficulty || 'medium'}`;
    const diffLabel = getDifficultyLabel(video.difficulty);
    const duration = formatDuration(video.duration_seconds);

    return `
        <div class="video-card" onclick="openVideo('${escapeAttr(video.url)}')">
            <span class="video-card-source ${sourceClass}">${sourceLabel}</span>
            <div class="video-card-title">${escapeHtml(video.title)}</div>
            <div class="video-card-meta">
                <span>📚 ${escapeHtml(video.topic || '')}</span>
                <span>⏱️ ${duration}</span>
                ${video.grade ? `<span>🎓 ${video.grade}</span>` : ''}
            </div>
            <span class="video-card-difficulty ${diffClass}">${diffLabel}</span>
            <div class="video-card-actions">
                <button onclick="event.stopPropagation(); openVideo('${escapeAttr(video.url)}')">▶ 재생</button>
                <button onclick="event.stopPropagation(); addToPlaylistPrompt(${video.id || 0})">+ 목록에 추가</button>
            </div>
        </div>
    `;
}

// ──────────────────────────────────────
// 재생목록
// ──────────────────────────────────────
const modalOverlay = document.getElementById('modal-overlay');
const createPlaylistBtn = document.getElementById('create-playlist-btn');
const modalClose = document.getElementById('modal-close');
const modalCancel = document.getElementById('modal-cancel');
const modalCreate = document.getElementById('modal-create');

createPlaylistBtn.addEventListener('click', () => modalOverlay.classList.add('active'));
modalClose.addEventListener('click', () => modalOverlay.classList.remove('active'));
modalCancel.addEventListener('click', () => modalOverlay.classList.remove('active'));
modalOverlay.addEventListener('click', e => {
    if (e.target === modalOverlay) modalOverlay.classList.remove('active');
});

modalCreate.addEventListener('click', async () => {
    const name = document.getElementById('playlist-name').value.trim();
    if (!name) return;

    const desc = document.getElementById('playlist-desc').value.trim();

    try {
        await API.post('/api/playlists/', { name, description: desc });
        modalOverlay.classList.remove('active');
        document.getElementById('playlist-name').value = '';
        document.getElementById('playlist-desc').value = '';
        loadPlaylists();
    } catch (err) {
        alert('재생목록 생성에 실패했습니다.');
    }
});

async function loadPlaylists() {
    const container = document.getElementById('playlists-container');

    try {
        const playlists = await API.get('/api/playlists/');

        if (playlists && playlists.length > 0) {
            container.innerHTML = playlists.map(p => `
                <div class="playlist-card" onclick="viewPlaylistDetail(${p.id})">
                    <div class="playlist-card-name">📋 ${escapeHtml(p.name)}</div>
                    <div class="playlist-card-desc">${escapeHtml(p.description || '설명 없음')}</div>
                    <div class="playlist-card-count">
                        <span>📺 ${p.video_count || 0}개 영상</span>
                    </div>
                </div>
            `).join('');
        } else {
            container.innerHTML = `
                <div class="empty-state">
                    <span class="empty-icon">📝</span>
                    <p>아직 재생목록이 없습니다. 새로 만들어 보세요!</p>
                </div>
            `;
        }
    } catch (err) {
        container.innerHTML = '<div class="empty-state"><span class="empty-icon">⚠️</span><p>로드 실패</p></div>';
    }
}

async function viewPlaylistDetail(id) {
    try {
        const detail = await API.get(`/api/playlists/${id}`);
        alert(`📋 ${detail.name}\n영상 ${detail.videos?.length || 0}개\n\n${detail.videos?.map(v => v.title).join('\n') || '영상 없음'}`);
    } catch (err) {
        alert('상세 조회 실패');
    }
}

function addToPlaylistPrompt(videoId) {
    alert('재생목록에 추가하려면 먼저 재생목록을 생성해 주세요!');
}

// ──────────────────────────────────────
// 대시보드
// ──────────────────────────────────────
async function loadDashboard() {
    try {
        const data = await API.get('/api/videos/dashboard/1');

        document.getElementById('stat-watched').textContent = data.total_watched;
        document.getElementById('stat-completed').textContent = data.total_completed;
        document.getElementById('stat-score').textContent = `${data.avg_quiz_score}점`;
        document.getElementById('stat-time').textContent = `${data.total_watch_time_minutes}분`;

        const weakList = document.getElementById('weak-topics-list');
        if (data.weak_topics && data.weak_topics.length > 0) {
            weakList.innerHTML = data.weak_topics.map(wt => `
                <div class="weak-topic-item">
                    <div class="weak-topic-info">
                        <h4>${escapeHtml(wt.topic)} — ${escapeHtml(wt.subtopic)}</h4>
                        <p>${escapeHtml(wt.recommendation)}</p>
                    </div>
                    <div class="weak-topic-score" style="color: ${getScoreColor(wt.avg_score)}">
                        ${wt.avg_score}점
                    </div>
                </div>
            `).join('');
        } else {
            weakList.innerHTML = `
                <div class="empty-state">
                    <span class="empty-icon">📈</span>
                    <p>학습 데이터가 쌓이면 취약 단원을 분석해 드려요</p>
                </div>
            `;
        }
    } catch (err) {
        console.error('대시보드 로드 실패:', err);
    }
}

// ──────────────────────────────────────
// 유틸리티
// ──────────────────────────────────────
function openVideo(url) {
    window.open(url, '_blank');
}

function escapeHtml(str) {
    if (!str) return '';
    const div = document.createElement('div');
    div.textContent = str;
    return div.innerHTML;
}

function escapeAttr(str) {
    if (!str) return '';
    return str.replace(/'/g, "\\'").replace(/"/g, '&quot;');
}

function getDifficultyLabel(diff) {
    const labels = { easy: '🟢 기초', medium: '🟡 보통', hard: '🔴 심화' };
    return labels[diff] || '🟡 보통';
}

function formatDuration(seconds) {
    if (!seconds) return '--:--';
    const m = Math.floor(seconds / 60);
    const s = seconds % 60;
    return `${m}:${s.toString().padStart(2, '0')}`;
}

function getScoreColor(score) {
    if (score < 30) return '#ff4757';
    if (score < 50) return '#ffa502';
    if (score < 70) return '#ffd93d';
    return '#2ed573';
}

// ──────────────────────────────────────
// 초기화
// ──────────────────────────────────────
console.log('✅ EBS 수학 영상 학습 추천 시스템 로드 완료');
