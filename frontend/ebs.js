/**
 * EBS Course Module
 * Handles EBS course filtering, recommendation display.
 */

let ebsLoaded = false;
let allEBSCourses = [];

// ──────────────────────────────────────────────
// Init EBS Filters
// ──────────────────────────────────────────────
document.addEventListener('DOMContentLoaded', () => {
    const filterBtns = document.querySelectorAll('#ebs-filters .filter-btn');
    filterBtns.forEach(btn => {
        btn.addEventListener('click', () => {
            // Update active filter
            filterBtns.forEach(b => b.classList.remove('active'));
            btn.classList.add('active');

            const level = btn.dataset.level;
            filterEBSCourses(level);
        });
    });
});

// ──────────────────────────────────────────────
// Load All EBS Courses
// ──────────────────────────────────────────────
async function loadEBSCourses() {
    if (ebsLoaded) return;

    const container = document.getElementById('ebs-results');
    container.innerHTML = '<div class="spinner"></div>';

    try {
        const data = await apiGet('/ebs/courses');
        allEBSCourses = data.courses || [];
        ebsLoaded = true;
        renderEBSGrid(allEBSCourses);
    } catch (err) {
        container.innerHTML = `
            <div class="empty-state">
                <span class="empty-icon">⚠️</span>
                <p>EBS 강좌를 불러올 수 없어요.<br>서버 연결을 확인해주세요.</p>
            </div>
        `;
    }
}

// ──────────────────────────────────────────────
// Filter EBS Courses
// ──────────────────────────────────────────────
function filterEBSCourses(level) {
    if (!level) {
        renderEBSGrid(allEBSCourses);
    } else {
        const filtered = allEBSCourses.filter(c => c.level === level);
        renderEBSGrid(filtered);
    }
}

// ──────────────────────────────────────────────
// Render EBS Grid
// ──────────────────────────────────────────────
function renderEBSGrid(courses) {
    const container = document.getElementById('ebs-results');

    if (!courses || courses.length === 0) {
        container.innerHTML = `
            <div class="empty-state">
                <span class="empty-icon">📚</span>
                <p>해당 조건에 맞는 강좌가 없어요.</p>
            </div>
        `;
        return;
    }

    container.innerHTML = courses.map(course => {
        const video = {
            video_id: course.id,
            title: course.title,
            channel: course.teacher,
            teacher: course.teacher,
            thumbnail: course.thumbnail,
            description: course.description,
            url: course.url,
            topics: course.topics,
            lectures: course.lectures,
            rating: course.rating,
        };
        return createVideoCard(video, 'ebs');
    }).join('');
}

// ──────────────────────────────────────────────
// Render EBS Results (from chat recommendations)
// ──────────────────────────────────────────────
function renderEBSResults(courses) {
    allEBSCourses = courses;
    ebsLoaded = true;
    renderEBSGrid(courses);
}
