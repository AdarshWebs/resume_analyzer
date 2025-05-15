document.addEventListener('DOMContentLoaded', function() {
    // Initialize score charts if we're on the results page
    const scoreChartCanvas = document.getElementById('scoreChart');
    const categoryScoresCanvas = document.getElementById('categoryScores');
    
    if (scoreChartCanvas) {
        renderScoreGauge(scoreChartCanvas);
    }
    
    if (categoryScoresCanvas) {
        renderCategoryScores(categoryScoresCanvas);
    }
});

function renderScoreGauge(canvas) {
    // Get overall score from data attribute
    const score = parseInt(canvas.getAttribute('data-score') || '0');
    
    // Define chart colors based on score
    let color;
    if (score >= 90) {
        color = '#28a745'; // Green (A)
    } else if (score >= 80) {
        color = '#5cb85c'; // Light green (B)
    } else if (score >= 70) {
        color = '#ffc107'; // Yellow (C)
    } else if (score >= 60) {
        color = '#fd7e14'; // Orange (D)
    } else {
        color = '#dc3545'; // Red (F)
    }
    
    // Create gauge chart
    new Chart(canvas, {
        type: 'doughnut',
        data: {
            datasets: [{
                data: [score, 100 - score],
                backgroundColor: [color, '#e9ecef'],
                borderWidth: 0
            }]
        },
        options: {
            cutout: '70%',
            circumference: 180,
            rotation: 270,
            responsive: true,
            maintainAspectRatio: true,
            plugins: {
                tooltip: {
                    enabled: false
                },
                legend: {
                    display: false
                }
            }
        }
    });
    
    // Add the score text in the center
    const scoreText = document.createElement('div');
    scoreText.classList.add('score-text');
    scoreText.innerHTML = `<span class="score-value">${score}</span><span class="score-label">/100</span>`;
    
    const canvasParent = canvas.parentElement;
    canvasParent.style.position = 'relative';
    scoreText.style.position = 'absolute';
    scoreText.style.bottom = '0';
    scoreText.style.left = '0';
    scoreText.style.width = '100%';
    scoreText.style.textAlign = 'center';
    scoreText.style.fontSize = '1.5rem';
    scoreText.style.fontWeight = 'bold';
    canvasParent.appendChild(scoreText);
}

function renderCategoryScores(canvas) {
    // Get category scores
    const categoriesData = JSON.parse(canvas.getAttribute('data-scores') || '{}');
    
    // Prepare data for radar chart
    const categories = [];
    const scores = [];
    
    if (categoriesData.sections) categories.push('Sections');
    if (categoriesData.sections) scores.push((categoriesData.sections / 30) * 100);
    
    if (categoriesData.keywords) categories.push('Keywords');
    if (categoriesData.keywords) scores.push((categoriesData.keywords / 25) * 100);
    
    if (categoriesData.action_verbs) categories.push('Action Verbs');
    if (categoriesData.action_verbs) scores.push((categoriesData.action_verbs / 20) * 100);
    
    if (categoriesData.word_count) categories.push('Content');
    if (categoriesData.word_count) scores.push((categoriesData.word_count / 15) * 100);
    
    if (categoriesData.issues) categories.push('Issues');
    if (categoriesData.issues) scores.push((categoriesData.issues / 10) * 100);
    
    // Create radar chart
    new Chart(canvas, {
        type: 'radar',
        data: {
            labels: categories,
            datasets: [{
                label: 'Score Percentage',
                data: scores,
                fill: true,
                backgroundColor: 'rgba(54, 162, 235, 0.2)',
                borderColor: 'rgb(54, 162, 235)',
                pointBackgroundColor: 'rgb(54, 162, 235)',
                pointBorderColor: '#fff',
                pointHoverBackgroundColor: '#fff',
                pointHoverBorderColor: 'rgb(54, 162, 235)'
            }]
        },
        options: {
            scales: {
                r: {
                    angleLines: {
                        display: true
                    },
                    suggestedMin: 0,
                    suggestedMax: 100
                }
            },
            plugins: {
                legend: {
                    display: false
                }
            }
        }
    });
}

// Function to create the skills comparison chart
function createSkillsComparisonChart(canvas, resumeSkills, jobSkills) {
    if (!canvas) return;
    
    // Parse the skills data
    const resumeSkillsList = JSON.parse(resumeSkills || '[]');
    const jobSkillsList = JSON.parse(jobSkills || '[]');
    
    // Find matching and missing skills
    const matchingSkills = resumeSkillsList.filter(skill => 
        jobSkillsList.includes(skill)
    );
    
    const missingSkills = jobSkillsList.filter(skill => 
        !resumeSkillsList.includes(skill)
    );
    
    const extraSkills = resumeSkillsList.filter(skill => 
        !jobSkillsList.includes(skill)
    );
    
    // Create the chart
    new Chart(canvas, {
        type: 'bar',
        data: {
            labels: ['Matching Skills', 'Missing Skills', 'Additional Skills'],
            datasets: [{
                label: 'Number of Skills',
                data: [matchingSkills.length, missingSkills.length, extraSkills.length],
                backgroundColor: [
                    'rgba(75, 192, 192, 0.2)',
                    'rgba(255, 99, 132, 0.2)',
                    'rgba(255, 206, 86, 0.2)'
                ],
                borderColor: [
                    'rgba(75, 192, 192, 1)',
                    'rgba(255, 99, 132, 1)',
                    'rgba(255, 206, 86, 1)'
                ],
                borderWidth: 1
            }]
        },
        options: {
            scales: {
                y: {
                    beginAtZero: true,
                    stepSize: 1
                }
            },
            plugins: {
                tooltip: {
                    callbacks: {
                        afterLabel: function(context) {
                            const index = context.dataIndex;
                            if (index === 0 && matchingSkills.length > 0) {
                                return '\n' + matchingSkills.join(', ');
                            } else if (index === 1 && missingSkills.length > 0) {
                                return '\n' + missingSkills.join(', ');
                            } else if (index === 2 && extraSkills.length > 0) {
                                return '\n' + extraSkills.join(', ');
                            }
                            return '';
                        }
                    }
                }
            }
        }
    });
}
