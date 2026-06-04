import re

file_path = r'c:\maxworth internship\templates\employee_profile.html'

with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

# Replace the single script block with a data block and multiple script blocks
old_script = """<script>
    const chartData = {{ profile_chart_data|tojson }};
    
    // Attendance Doughnut Chart
    const ctxAtt = document.getElementById('attendanceChart').getContext('2d');
    new Chart(ctxAtt, {
        type: 'doughnut',
        data: {
            labels: chartData.holiday_labels,
            datasets: [{
                data: chartData.holiday_counts,
                backgroundColor: ['#198754', '#ffc107', '#0dcaf0', '#dc3545'],
                borderWidth: 0,
                hoverOffset: 4
            }]
        },
        options: {
            responsive: true,
            cutout: '75%',
            plugins: {
                legend: { display: false }
            }
        }
    });

    {% if tenure_years >= 1 %}
    // Performance Bar Chart
    const ctxPerf = document.getElementById('performanceChart').getContext('2d');
    new Chart(ctxPerf, {
        type: 'bar',
        data: {
            labels: chartData.performance_labels,
            datasets: [{
                label: 'Performance Score',
                data: chartData.performance_scores,
                backgroundColor: 'rgba(13, 110, 253, 0.8)',
                borderRadius: 4,
                barThickness: 30
            }]
        },
        options: {
            responsive: true,
            scales: {
                y: {
                    beginAtZero: true,
                    max: 100,
                    grid: { borderDash: [2, 4], color: '#f0f0f0' }
                },
                x: {
                    grid: { display: false }
                }
            },
            plugins: {
                legend: { display: false }
            }
        }
    });
    {% endif %}
</script>"""

new_script = """<script id="profile-chart-data" type="application/json">
{{ profile_chart_data|tojson|safe }}
</script>
<script>
    const chartData = JSON.parse(document.getElementById('profile-chart-data').textContent);
    
    // Attendance Doughnut Chart
    const ctxAtt = document.getElementById('attendanceChart').getContext('2d');
    new Chart(ctxAtt, {
        type: 'doughnut',
        data: {
            labels: chartData.holiday_labels,
            datasets: [{
                data: chartData.holiday_counts,
                backgroundColor: ['#198754', '#ffc107', '#0dcaf0', '#dc3545'],
                borderWidth: 0,
                hoverOffset: 4
            }]
        },
        options: {
            responsive: true,
            cutout: '75%',
            plugins: {
                legend: { display: false }
            }
        }
    });
</script>

{% if tenure_years >= 1 %}
<script>
    // Performance Bar Chart
    const ctxPerf = document.getElementById('performanceChart').getContext('2d');
    new Chart(ctxPerf, {
        type: 'bar',
        data: {
            labels: chartData.performance_labels,
            datasets: [{
                label: 'Performance Score',
                data: chartData.performance_scores,
                backgroundColor: 'rgba(13, 110, 253, 0.8)',
                borderRadius: 4,
                barThickness: 30
            }]
        },
        options: {
            responsive: true,
            scales: {
                y: {
                    beginAtZero: true,
                    max: 100,
                    grid: { borderDash: [2, 4], color: '#f0f0f0' }
                },
                x: {
                    grid: { display: false }
                }
            },
            plugins: {
                legend: { display: false }
            }
        }
    });
</script>
{% endif %}"""

if old_script in content:
    content = content.replace(old_script, new_script)
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    print("Script syntax fixed.")
else:
    print("Could not find the script block. Trying regex.")
    # Fallback to general replacement
    content = content.replace("const chartData = {{ profile_chart_data|tojson }};", 
                              "const chartDataRaw = document.getElementById('profile-chart-data').textContent; const chartData = JSON.parse(chartDataRaw);")
    
    # Needs <script id="profile-chart-data"> inserted before <script>
    # This might be tricky, so let's stick to the exact string replace, which should work if nothing else modified it.
