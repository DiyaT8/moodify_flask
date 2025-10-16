document.addEventListener('DOMContentLoaded', () => {

    // ---------------- Preset Mood Buttons ----------------
    document.querySelectorAll('.preset').forEach(btn => {
        btn.addEventListener('click', () => {
            document.getElementById('mood_text').value = btn.textContent;
        });
    });

    // ---------------- Voice Input ----------------
    document.getElementById('voiceBtn').addEventListener('click', () => {
        const recognition = new (window.SpeechRecognition || window.webkitSpeechRecognition)();
        recognition.lang = 'en-US';
        recognition.start();
        recognition.onresult = (event) => {
            document.getElementById('mood_text').value = event.results[0][0].transcript;
        };
    });

    // ---------------- Submit Mood ----------------
    const logoContainer = document.getElementById('logoContainer');
    const formContainer = document.getElementById('formContainer');
    const resultsSection = document.getElementById('resultsSection');

    document.getElementById('submitBtn').addEventListener('click', async () => {
        const text = document.getElementById('mood_text').value.trim();
        if(!text) return;

        // Animate logo to center
        logoContainer.classList.add('active');
        document.body.classList.add('blur');

        // Simulate analysis delay
        setTimeout(async () => {
            const formData = new FormData();
            formData.append('mood_text', text);

            try {
                const resp = await fetch('/recommend', { method:'POST', body:formData });
                const data = await resp.json();
                if(data.error){ alert(data.error); return; }

                // Fill results
                const resultsDiv = document.getElementById('results');
                resultsDiv.innerHTML = '';
                (data.results || []).forEach(track => {
                    const a = document.createElement('a');
                    a.href = track.url;
                    a.target = "_blank";
                    a.className = 'song-card';
                    a.innerHTML = `
                        <img src="${track.thumbnail}" alt="${track.title}">
                        <div class="song-info">
                            <div class="song-title">${track.title}</div>
                            <div class="song-artist">${track.artist}</div>
                        </div>
                    `;
                    resultsDiv.appendChild(a);
                });

                // Animate logo back to left and fade out
                logoContainer.classList.remove('active');
                logoContainer.classList.add('fade-out');
                document.body.classList.remove('blur');

                // Show results after fade-out
                setTimeout(() => {
                    formContainer.style.display = 'none';
                    resultsSection.style.display = 'block';
                }, 1000);

            } catch(err){
                console.error(err);
                alert("Something went wrong while fetching recommendations.");
            }
        }, 1500);
    });

    // ---------------- Analyze Again ----------------
    document.getElementById('analyzeAgain').addEventListener('click', () => {
        resultsSection.style.display = 'none';
        formContainer.style.display = 'flex';
        document.getElementById('mood_text').value = '';

        // Reset logo
        logoContainer.classList.remove('fade-out');
    });
});
