// Bedtime Stories - Frontend logic
document.addEventListener('DOMContentLoaded', function() {
    // Elements
    const storyDateEl = document.getElementById('storyDate');
    const englishTextEl = document.getElementById('englishText');
    const chineseTextEl = document.getElementById('chineseText');
    const previousStoriesEl = document.getElementById('previousStories');
    const langButtons = document.querySelectorAll('.lang-btn');
    const shareBtn = document.getElementById('shareBtn');
    const storyContent = document.querySelector('.story-content');

    // Current date in YYYY-MM-DD
    const today = new Date().toISOString().split('T')[0];
    const todayFormatted = new Date().toLocaleDateString('en-US', {
        weekday: 'long',
        year: 'numeric',
        month: 'long',
        day: 'numeric'
    });

    // Language toggle
    langButtons.forEach(btn => {
        btn.addEventListener('click', function() {
            langButtons.forEach(b => b.classList.remove('active'));
            this.classList.add('active');
            const lang = this.dataset.lang;
            // Show/hide language sections
            if (lang === 'both') {
                document.querySelectorAll('[data-lang]').forEach(el => {
                    el.style.display = 'block';
                });
                storyContent.style.gridTemplateColumns = '1fr 1fr';
                if (window.innerWidth <= 640) {
                    storyContent.style.gridTemplateColumns = '1fr';
                }
            } else if (lang === 'en') {
                document.querySelector('[data-lang="en"]').style.display = 'block';
                document.querySelector('[data-lang="zh"]').style.display = 'none';
                storyContent.style.gridTemplateColumns = '1fr';
            } else if (lang === 'zh') {
                document.querySelector('[data-lang="en"]').style.display = 'none';
                document.querySelector('[data-lang="zh"]').style.display = 'block';
                storyContent.style.gridTemplateColumns = '1fr';
            }
        });
    });

    // Share button
    if (navigator.share) {
        shareBtn.addEventListener('click', async () => {
            try {
                await navigator.share({
                    title: 'Pipi\'s Bedtime Stories',
                    text: 'A heartwarming bilingual story to enjoy before sleep.',
                    url: window.location.href
                });
            } catch (err) {
                console.log('Share cancelled:', err);
            }
        });
    } else {
        // Fallback: copy URL to clipboard
        shareBtn.addEventListener('click', () => {
            navigator.clipboard.writeText(window.location.href).then(() => {
                const originalText = shareBtn.textContent;
                shareBtn.textContent = '✅ Copied!';
                setTimeout(() => {
                    shareBtn.textContent = originalText;
                }, 2000);
            });
        });
    }

    // Load stories from JSON
    fetch('stories.json')
        .then(response => {
            if (!response.ok) throw new Error('Network response was not ok');
            return response.json();
        })
        .then(data => {
            if (!Array.isArray(data) || data.length === 0) {
                throw new Error('No stories found');
            }
            // Sort by date descending
            const sorted = data.sort((a, b) => new Date(b.date) - new Date(a.date));
            const latest = sorted[0];
            // If today's story exists, use it; else use latest
            const todayStory = sorted.find(s => s.date === today) || latest;

            // Display today's story
            storyDateEl.textContent = todayFormatted;
            englishTextEl.textContent = todayStory.en || 'Story not available.';
            chineseTextEl.textContent = todayStory.zh || '故事暂不可用。';

            // Display previous stories (excluding today's)
            const previous = sorted.filter(s => s.date !== today).slice(0, 5);
            if (previous.length > 0) {
                previousStoriesEl.innerHTML = '';
                previous.forEach(story => {
                    const date = new Date(story.date).toLocaleDateString('en-US', {
                        month: 'short',
                        day: 'numeric',
                        year: 'numeric'
                    });
                    const snippet = (story.en || '').substring(0, 120) + '...';
                    const div = document.createElement('div');
                    div.className = 'prev-story-item';
                    div.innerHTML = `
                        <div class="prev-story-date">${date}</div>
                        <div class="prev-story-snippet">${snippet}</div>
                    `;
                    previousStoriesEl.appendChild(div);
                });
            } else {
                previousStoriesEl.innerHTML = '<p>No previous stories yet. Check back tomorrow!</p>';
            }
        })
        .catch(error => {
            console.error('Failed to load stories:', error);
            storyDateEl.textContent = todayFormatted;
            englishTextEl.textContent = 'Oops! The story couldn’t be loaded. Please refresh the page.';
            chineseTextEl.textContent = '哎呀！故事加载失败，请刷新页面。';
            previousStoriesEl.innerHTML = '<p>Unable to load previous stories.</p>';
        });

    // Responsive grid adjustment
    function adjustGrid() {
        if (window.innerWidth <= 640 && document.querySelector('.lang-btn.active').dataset.lang === 'both') {
            storyContent.style.gridTemplateColumns = '1fr';
        } else if (document.querySelector('.lang-btn.active').dataset.lang === 'both') {
            storyContent.style.gridTemplateColumns = '1fr 1fr';
        }
    }
    window.addEventListener('resize', adjustGrid);
    adjustGrid();
});