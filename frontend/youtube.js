/**
 * YouTube Search Module
 * Handles YouTube video search and result display.
 */

let ytSearchInitialized = false;

// ──────────────────────────────────────────────
// Init YouTube Search UI
// ──────────────────────────────────────────────
function initYouTubeSearch() {
    if (ytSearchInitialized) return;
    ytSearchInitialized = true;

    const input = document.getElementById('yt-search-input');
    const btn = document.getElementById('yt-search-btn');

    btn.addEventListener('click', () => {
        const query = input.value.trim();
        if (query) searchYouTube(query);
    });

    input.addEventListener('keydown', (e) => {
        if (e.key === 'Enter') {
            const query = input.value.trim();
            if (query) searchYouTube(query);
        }
    });
}

// Make sure to init when DOM is ready
document.addEventListener('DOMContentLoaded', initYouTubeSearch);

// ──────────────────────────────────────────────
// Search YouTube
// ──────────────────────────────────────────────
async function searchYouTube(query) {
    const resultsContainer = document.getElementById('yt-results');
    const searchInput = document.getElementById('yt-search-input');

    // Set search input value
    searchInput.value = query;

    // Show loading
    resultsContainer.innerHTML = '<div class="spinner"></div>';

    try {
        const data = await apiPost('/youtube/search', {
            query: query,
            max_results: 6,
        });

        if (!data.results || data.results.length === 0) {
            resultsContainer.innerHTML = `
                <div class="empty-state">
                    <span class="empty-icon">🔍</span>
                    <p>"${query}"에 대한 결과를 찾지 못했어요.<br>다른 키워드로 검색해보세요!</p>
                </div>
            `;
            return;
        }

        // Render video cards
        resultsContainer.innerHTML = data.results.map(video => 
            createVideoCard(video, 'youtube')
        ).join('');

        // Add "YouTube에서 더 보기" link
        if (data.search_url) {
            resultsContainer.innerHTML += `
                <div class="empty-state" style="padding: 20px;">
                    <a href="${data.search_url}" target="_blank" 
                       class="card-btn btn-primary" style="text-decoration:none; padding: 12px 24px;">
                        🔗 YouTube에서 더 검색하기
                    </a>
                </div>
            `;
        }

    } catch (err) {
        resultsContainer.innerHTML = `
            <div class="empty-state">
                <span class="empty-icon">⚠️</span>
                <p>검색 중 오류가 발생했어요.<br>서버 연결을 확인해주세요.</p>
            </div>
        `;
    }
}
