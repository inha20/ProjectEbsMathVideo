/**
 * MathVideo AI - Main Application Controller
 * Handles tab navigation, API communication, and shared utilities.
 */

const API_BASE = 'http://localhost:8000/api';

// ──────────────────────────────────────────────
// Global State
// ──────────────────────────────────────────────
const AppState = {
    sessionId: null,
    currentTab: 'chat',
    playlist: [],
};

// ──────────────────────────────────────────────
// Tab Navigation
// ──────────────────────────────────────────────
function initNavigation() {
    const navBtns = document.querySelectorAll('.nav-btn');
    navBtns.forEach(btn => {
        btn.addEventListener('click', () => {
            const tab = btn.dataset.tab;
            switchTab(tab);
        });
    });
}

function switchTab(tab) {
    AppState.currentTab = tab;

    // Update nav buttons
    document.querySelectorAll('.nav-btn').forEach(btn => {
        btn.classList.toggle('active', btn.dataset.tab === tab);
    });

    // Update panels
    document.querySelectorAll('.panel').forEach(panel => {
        panel.classList.toggle('active', panel.id === `panel-${tab}`);
    });

    // Trigger tab-specific init
    if (tab === 'ebs' && typeof loadEBSCourses === 'function') {
        loadEBSCourses();
    }
}

// ──────────────────────────────────────────────
// API Helpers
// ──────────────────────────────────────────────
async function apiPost(endpoint, data = {}) {
    try {
        const resp = await fetch(`${API_BASE}${endpoint}`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data),
        });
        if (!resp.ok) throw new Error(`API error: ${resp.status}`);
        return await resp.json();
    } catch (err) {
        console.error('API POST error:', err);
        throw err;
    }
}

async function apiGet(endpoint) {
    try {
        const resp = await fetch(`${API_BASE}${endpoint}`);
        if (!resp.ok) throw new Error(`API error: ${resp.status}`);
        return await resp.json();
    } catch (err) {
        console.error('API GET error:', err);
        throw err;
    }
}

async function apiDelete(endpoint) {
    try {
        const resp = await fetch(`${API_BASE}${endpoint}`, { method: 'DELETE' });
        if (!resp.ok) throw new Error(`API error: ${resp.status}`);
        return await resp.json();
    } catch (err) {
        console.error('API DELETE error:', err);
        throw err;
    }
}

// ──────────────────────────────────────────────
// Toast Notifications
// ──────────────────────────────────────────────
function showToast(message, type = 'info') {
    const container = document.getElementById('toast-container');
    const icons = { success: '✅', error: '❌', info: 'ℹ️' };

    const toast = document.createElement('div');
    toast.className = `toast ${type}`;
    toast.innerHTML = `<span>${icons[type] || 'ℹ️'}</span><span>${message}</span>`;
    container.appendChild(toast);

    setTimeout(() => {
        toast.classList.add('toast-out');
        setTimeout(() => toast.remove(), 300);
    }, 3000);
}

// ──────────────────────────────────────────────
// Playlist Badge
// ──────────────────────────────────────────────
function updatePlaylistBadge() {
    const badge = document.getElementById('playlist-badge');
    const count = AppState.playlist.length;
    if (count > 0) {
        badge.textContent = count;
        badge.style.display = 'flex';
    } else {
        badge.style.display = 'none';
    }
}

// ──────────────────────────────────────────────
// Playlist Management
// ──────────────────────────────────────────────
async function addToPlaylist(video) {
    try {
        const resp = await apiPost('/playlist/add', {
            session_id: AppState.sessionId,
            video_id: video.video_id,
            title: video.title,
            channel: video.channel,
            thumbnail: video.thumbnail,
            source: video.source || 'youtube',
            url: video.url,
        });

        AppState.playlist = resp.playlist;
        updatePlaylistBadge();
        showToast('재생목록에 추가했어요!', 'success');

        // Update button state
        const btn = document.querySelector(`[data-vid="${video.video_id}"] .btn-secondary`);
        if (btn) {
            btn.className = 'card-btn btn-added';
            btn.innerHTML = '✅ 추가됨';
        }
    } catch (err) {
        showToast('추가에 실패했어요.', 'error');
    }
}

async function removeFromPlaylist(videoId) {
    try {
        const resp = await apiDelete(`/playlist/${AppState.sessionId}/${videoId}`);
        AppState.playlist = resp.playlist;
        updatePlaylistBadge();
        renderPlaylist();
        showToast('삭제되었어요.', 'info');
    } catch (err) {
        showToast('삭제에 실패했어요.', 'error');
    }
}

async function clearPlaylist() {
    if (!confirm('재생목록을 모두 삭제할까요?')) return;
    try {
        const resp = await apiDelete(`/playlist/${AppState.sessionId}`);
        AppState.playlist = [];
        updatePlaylistBadge();
        renderPlaylist();
        showToast('재생목록을 비웠어요.', 'info');
    } catch (err) {
        showToast('삭제에 실패했어요.', 'error');
    }
}

function renderPlaylist() {
    const container = document.getElementById('playlist-list');
    if (AppState.playlist.length === 0) {
        container.innerHTML = `
            <div class="empty-state">
                <span class="empty-icon">📋</span>
                <p>아직 재생목록이 비어있어요.<br>영상 카드에서 ➕ 버튼을 눌러 추가해보세요!</p>
            </div>
        `;
        return;
    }

    container.innerHTML = AppState.playlist.map((item, i) => `
        <div class="playlist-item" data-vid="${item.video_id}">
            <span class="pl-num">${i + 1}</span>
            <div class="pl-thumb">
                <img src="${item.thumbnail}" alt="" loading="lazy"
                     onerror="this.src='data:image/svg+xml,<svg xmlns=%22http://www.w3.org/2000/svg%22 viewBox=%220 0 320 180%22><rect fill=%22%230f1724%22 width=%22320%22 height=%22180%22/><text fill=%22%235a6478%22 font-size=%2224%22 x=%22160%22 y=%2296%22 text-anchor=%22middle%22>📐</text></svg>'">
            </div>
            <div class="pl-info">
                <div class="pl-title">${item.title}</div>
                <div class="pl-channel">${item.channel} · ${item.source === 'ebs' ? 'EBS' : 'YouTube'}</div>
            </div>
            <a href="${item.url}" target="_blank" class="card-btn btn-secondary" style="flex:0;padding:8px 12px;">▶️</a>
            <button class="pl-remove" onclick="removeFromPlaylist('${item.video_id}')" title="삭제">✕</button>
        </div>
    `).join('');
}

function exportPlaylist() {
    if (AppState.playlist.length === 0) {
        showToast('재생목록이 비어있어요.', 'info');
        return;
    }

    const ytItems = AppState.playlist.filter(v => v.source !== 'ebs');
    const ebsItems = AppState.playlist.filter(v => v.source === 'ebs');

    let linksHtml = '';

    if (ytItems.length > 0) {
        const videoIds = ytItems.map(v => v.video_id).join(',');
        const ytPlaylistUrl = `https://www.youtube.com/watch_videos?video_ids=${videoIds}`;
        linksHtml += `
            <div class="modal-link-item">
                <span>▶️</span>
                <a href="${ytPlaylistUrl}" target="_blank">YouTube 연속 재생 (${ytItems.length}개)</a>
            </div>
        `;
    }

    ebsItems.forEach(item => {
        linksHtml += `
            <div class="modal-link-item">
                <span>📚</span>
                <a href="${item.url}" target="_blank">${item.title}</a>
            </div>
        `;
    });

    // Show modal
    const overlay = document.createElement('div');
    overlay.className = 'modal-overlay';
    overlay.innerHTML = `
        <div class="modal">
            <h3>📤 재생목록 내보내기</h3>
            <p>아래 링크를 클릭하면 영상을 바로 볼 수 있어요!</p>
            <div class="modal-links">${linksHtml}</div>
            <button class="modal-close">닫기</button>
        </div>
    `;

    document.body.appendChild(overlay);
    overlay.querySelector('.modal-close').addEventListener('click', () => overlay.remove());
    overlay.addEventListener('click', (e) => {
        if (e.target === overlay) overlay.remove();
    });
}

// ──────────────────────────────────────────────
// Video Card Renderer (shared)
// ──────────────────────────────────────────────
function createVideoCard(video, source = 'youtube') {
    const isInPlaylist = AppState.playlist.some(v => v.video_id === video.video_id);
    const addBtnClass = isInPlaylist ? 'card-btn btn-added' : 'card-btn btn-secondary';
    const addBtnText = isInPlaylist ? '✅ 추가됨' : '➕ 재생목록';

    return `
        <div class="video-card" data-vid="${video.video_id}">
            <div class="thumb">
                <img src="${video.thumbnail}" alt="${video.title}" loading="lazy"
                     onerror="this.src='data:image/svg+xml,<svg xmlns=%22http://www.w3.org/2000/svg%22 viewBox=%220 0 320 180%22><rect fill=%22%230f1724%22 width=%22320%22 height=%22180%22/><text fill=%22%235a6478%22 font-size=%2224%22 x=%22160%22 y=%2296%22 text-anchor=%22middle%22>📐</text></svg>'">
                <span class="source-badge ${source}">${source === 'ebs' ? 'EBS' : 'YouTube'}</span>
            </div>
            <div class="card-body">
                <div class="card-title">${video.title}</div>
                <div class="card-channel">${video.channel || video.teacher || ''}</div>
                ${video.view_count ? `<div class="card-meta"><span>👁️ ${video.view_count}</span></div>` : ''}
                ${video.topics ? `
                    <div class="ebs-card-tags">
                        ${video.topics.slice(0, 4).map(t => `<span class="ebs-tag">${t}</span>`).join('')}
                    </div>
                ` : ''}
                ${video.lectures ? `
                    <div class="ebs-card-info">
                        <span>📖 ${video.lectures}강</span>
                        ${video.rating ? `<span class="ebs-rating">⭐ ${video.rating}</span>` : ''}
                    </div>
                ` : ''}
                <div class="card-actions">
                    <a href="${video.url}" target="_blank" class="card-btn btn-primary">▶️ 보러가기</a>
                    <button class="${addBtnClass}" onclick="addToPlaylist({
                        video_id: '${video.video_id || video.id}',
                        title: \`${video.title.replace(/`/g, '\\`')}\`,
                        channel: '${(video.channel || video.teacher || '').replace(/'/g, "\\'")}',
                        thumbnail: '${video.thumbnail}',
                        source: '${source}',
                        url: '${video.url}'
                    })">${addBtnText}</button>
                </div>
            </div>
        </div>
    `;
}

// ──────────────────────────────────────────────
// Init
// ──────────────────────────────────────────────
document.addEventListener('DOMContentLoaded', () => {
    initNavigation();

    // Playlist buttons
    document.getElementById('playlist-clear-btn').addEventListener('click', clearPlaylist);
    document.getElementById('playlist-export-btn').addEventListener('click', exportPlaylist);

    // Init chat (defined in chat.js)
    if (typeof initChat === 'function') {
        initChat();
    }
});
