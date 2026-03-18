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

    // Play button for narration
    const playBtn = document.getElementById('playBtn');
    let currentSpeech = null;
    let isPlaying = false;

    // Initialize speech synthesis
    function initSpeech() {
        if ('speechSynthesis' in window) {
            // Speech synthesis is available
            return true;
        } else {
            console.warn('Speech synthesis not supported');
            playBtn.disabled = true;
            playBtn.title = 'Text-to-speech not supported in your browser';
            return false;
        }
    }

    // Get appropriate voice for language
    function getVoiceForLang(lang) {
        const voices = speechSynthesis.getVoices();
        // Prefer female voices for young tone
        const femaleVoices = voices.filter(v => 
            v.lang.startsWith(lang === 'zh' ? 'zh' : 'en') && 
            v.name.toLowerCase().includes('female')
        );
        if (femaleVoices.length > 0) return femaleVoices[0];
        
        // Fallback to any voice for the language
        const langVoices = voices.filter(v => v.lang.startsWith(lang === 'zh' ? 'zh' : 'en'));
        if (langVoices.length > 0) return langVoices[0];
        
        // Fallback to default
        return voices.find(v => v.default) || voices[0];
    }

    // Speak text
    function speakText(text, lang) {
        if (!text) return;
        
        stopSpeech();
        
        const utterance = new SpeechSynthesisUtterance(text);
        utterance.lang = lang === 'zh' ? 'zh-CN' : 'en-US';
        utterance.rate = 0.9; // Slightly slower for bedtime story
        utterance.pitch = 1.1; // Slightly higher for young voice
        utterance.volume = 1;
        
        const voice = getVoiceForLang(lang);
        if (voice) utterance.voice = voice;
        
        utterance.onstart = () => {
            isPlaying = true;
            playBtn.classList.add('playing');
            playBtn.innerHTML = '<span class="play-icon">⏸️</span> Stop';
        };
        
        utterance.onend = utterance.onerror = () => {
            isPlaying = false;
            playBtn.classList.remove('playing');
            playBtn.innerHTML = '<span class="play-icon">▶️</span> Listen';
            currentSpeech = null;
        };
        
        speechSynthesis.speak(utterance);
        currentSpeech = utterance;
    }

    // Stop current speech
    function stopSpeech() {
        if (currentSpeech) {
            speechSynthesis.cancel();
            currentSpeech = null;
        }
        isPlaying = false;
        playBtn.classList.remove('playing');
        playBtn.innerHTML = '<span class="play-icon">▶️</span> Listen';
    }

    // Toggle play/pause
    function togglePlay() {
        if (!initSpeech()) return;
        
        if (isPlaying) {
            stopSpeech();
            return;
        }
        
        const activeLang = document.querySelector('.lang-btn.active').dataset.lang;
        let textToSpeak = '';
        let lang = 'en';
        
        if (activeLang === 'en') {
            textToSpeak = englishTextEl.textContent;
            lang = 'en';
        } else if (activeLang === 'zh') {
            textToSpeak = chineseTextEl.textContent;
            lang = 'zh';
        } else if (activeLang === 'both') {
            // Speak both languages (English first)
            textToSpeak = englishTextEl.textContent + '\n\n' + chineseTextEl.textContent;
            lang = 'en'; // Will switch for Chinese part? Simpler: just speak English for now
            // For simplicity, we'll just speak English
            textToSpeak = englishTextEl.textContent;
            lang = 'en';
        }
        
        if (textToSpeak && textToSpeak !== 'Loading story...' && textToSpeak !== '正在加载故事...') {
            speakText(textToSpeak, lang);
        }
    }

    // Initialize speech when voices are loaded
    if ('speechSynthesis' in window) {
        speechSynthesis.onvoiceschanged = initSpeech;
    }
    
    playBtn.addEventListener('click', togglePlay);

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

            // Store stories for later use
            window.storiesData = {
                allStories: sorted,
                todayStory: todayStory,
                today: today
            };

            // Function to display a story in the main card
            function displayStory(story, isToday = false) {
                const storyDate = new Date(story.date);
                const formattedDate = storyDate.toLocaleDateString('en-US', {
                    weekday: 'long',
                    year: 'numeric',
                    month: 'long',
                    day: 'numeric'
                });
                
                storyDateEl.textContent = formattedDate;
                englishTextEl.textContent = story.en || 'Story not available.';
                chineseTextEl.textContent = story.zh || '故事暂不可用。';
                
                // Update header based on whether it's today's story
                const storyHeader = document.querySelector('.story-date h2');
                if (storyHeader) {
                    storyHeader.textContent = isToday ? 'Tonight\'s Story' : 'Story from ' + storyDate.toLocaleDateString('en-US', { month: 'short', day: 'numeric' });
                }
                
                // Show/hide back button
                const backBtn = document.getElementById('backToTodayBtn');
                if (backBtn) {
                    backBtn.style.display = isToday ? 'none' : 'block';
                }
                
                // Update play button to work with this story
                // (play button already uses englishTextEl and chineseTextEl)
            }

            // Create back button if it doesn't exist
            let backBtn = document.getElementById('backToTodayBtn');
            if (!backBtn) {
                backBtn = document.createElement('button');
                backBtn.id = 'backToTodayBtn';
                backBtn.className = 'back-today-btn';
                backBtn.innerHTML = '← Back to today\'s story';
                backBtn.style.display = 'none';
                backBtn.addEventListener('click', () => {
                    displayStory(todayStory, true);
                });
                document.querySelector('.story-date').appendChild(backBtn);
            }

            // Display previous stories (excluding today's)
            const allPrevious = sorted.filter(s => s.date !== today);
            const recentPrevious = allPrevious.slice(0, 2); // Only show 2 explicitly
            const olderStories = allPrevious.slice(2); // Archive for older stories
            
            if (allPrevious.length > 0) {
                previousStoriesEl.innerHTML = '';
                
                // Display recent previous stories (up to 2)
                if (recentPrevious.length > 0) {
                    recentPrevious.forEach(story => {
                        const date = new Date(story.date).toLocaleDateString('en-US', {
                            month: 'short',
                            day: 'numeric',
                            year: 'numeric'
                        });
                        const snippet = (story.en || '').substring(0, 120) + '...';
                        const div = document.createElement('div');
                        div.className = 'prev-story-item clickable';
                        div.dataset.date = story.date;
                        div.innerHTML = `
                            <div class="prev-story-date">${date}</div>
                            <div class="prev-story-snippet">${snippet}</div>
                            <div class="prev-story-click-hint">Tap to read →</div>
                        `;
                        div.addEventListener('click', () => {
                            displayStory(story, false);
                            // Scroll to top of story card
                            document.querySelector('.story-card').scrollIntoView({ behavior: 'smooth' });
                        });
                        previousStoriesEl.appendChild(div);
                    });
                }
                
                // Display archive for older stories
                if (olderStories.length > 0) {
                    const archiveSection = document.createElement('div');
                    archiveSection.className = 'archive-section';
                    archiveSection.innerHTML = `
                        <h3>Older Stories (${olderStories.length})</h3>
                        <div class="archive-list"></div>
                    `;
                    previousStoriesEl.appendChild(archiveSection);
                    
                    const archiveList = archiveSection.querySelector('.archive-list');
                    olderStories.forEach(story => {
                        const date = new Date(story.date).toLocaleDateString('en-US', {
                            month: 'short',
                            day: 'numeric',
                            year: 'numeric'
                        });
                        const div = document.createElement('div');
                        div.className = 'archive-item';
                        div.dataset.date = story.date;
                        div.innerHTML = `
                            <span class="archive-date">${date}</span>
                            <span class="archive-snippet">${(story.en || '').substring(0, 80)}...</span>
                        `;
                        div.addEventListener('click', () => {
                            displayStory(story, false);
                            document.querySelector('.story-card').scrollIntoView({ behavior: 'smooth' });
                        });
                        archiveList.appendChild(div);
                    });
                }
                
                // If no recent stories but there are older ones (unlikely)
                if (recentPrevious.length === 0 && olderStories.length > 0) {
                    previousStoriesEl.innerHTML = '<p>No recent stories. Check the archive below.</p>';
                }
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