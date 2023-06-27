class PcSoftUiDashboardTmp extends PcAddOn {

    get sidenavScrollbar() {
        return document.querySelector('#sidenav-scrollbar')
    }
    
    get ctx() {
        return document.getElementById("chart-bars").getContext("2d")
    }
    
    get ctx2() {
        return document.getElementById("chart-line").getContext("2d")
    }
    
    initialize = () => {
        this.#windowsFix()
        this.#initializeChart()
    }

    #windowsFix = () => {
        const win = navigator.platform.includes('Win')
        if (win && this.sidenavScrollbar) {
          const options = {
            damping: '0.5'
          }
          Scrollbar.init(this.sidenavScrollbar, options)
        }
    }
    
    #initializeChart = () => {
        if (!this.ctx || !this.ctx2) {
            return
        }
        new Chart(this.ctx, {
          type: "bar",
          data: {
            labels: ["Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"],
            datasets: [{
              label: "Sales",
              tension: 0.4,
              borderWidth: 0,
              borderRadius: 4,
              borderSkipped: false,
              backgroundColor: "#fff",
              data: [450, 200, 100, 220, 500, 100, 400, 230, 500],
              maxBarThickness: 6
            }, ],
          },
          options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
              legend: {
                display: false,
              }
            },
            interaction: {
              intersect: false,
              mode: 'index',
            },
            scales: {
              y: {
                grid: {
                  drawBorder: false,
                  display: false,
                  drawOnChartArea: false,
                  drawTicks: false,
                },
                ticks: {
                  suggestedMin: 0,
                  suggestedMax: 500,
                  beginAtZero: true,
                  padding: 15,
                  font: {
                    size: 14,
                    family: "Open Sans",
                    style: 'normal',
                    lineHeight: 2
                  },
                  color: "#fff"
                },
              },
              x: {
                grid: {
                  drawBorder: false,
                  display: false,
                  drawOnChartArea: false,
                  drawTicks: false
                },
                ticks: {
                  display: false
                },
              },
            },
          },
        })
    
        var gradientStroke1 = this.ctx2.createLinearGradient(0, 230, 0, 50)
    
        gradientStroke1.addColorStop(1, 'rgba(203,12,159,0.2)')
        gradientStroke1.addColorStop(0.2, 'rgba(72,72,176,0.0)')
        gradientStroke1.addColorStop(0, 'rgba(203,12,159,0)') //purple colors
    
        var gradientStroke2 = this.ctx2.createLinearGradient(0, 230, 0, 50)
    
        gradientStroke2.addColorStop(1, 'rgba(20,23,39,0.2)')
        gradientStroke2.addColorStop(0.2, 'rgba(72,72,176,0.0)')
        gradientStroke2.addColorStop(0, 'rgba(20,23,39,0)') //purple colors
    
        new Chart(this.ctx2, {
          type: "line",
          data: {
            labels: ["Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"],
            datasets: [{
                label: "Mobile apps",
                tension: 0.4,
                pointRadius: 0,
                borderColor: "#cb0c9f",
                borderWidth: 3,
                backgroundColor: gradientStroke1,
                fill: true,
                data: [50, 40, 300, 220, 500, 250, 400, 230, 500],
                maxBarThickness: 6
    
              },
              {
                label: "Websites",
                tension: 0.4,
                pointRadius: 0,
                borderColor: "#3A416F",
                borderWidth: 3,
                backgroundColor: gradientStroke2,
                fill: true,
                data: [30, 90, 40, 140, 290, 290, 340, 230, 400],
                maxBarThickness: 6
              },
            ],
          },
          options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
              legend: {
                display: false,
              }
            },
            interaction: {
              intersect: false,
              mode: 'index',
            },
            scales: {
              y: {
                grid: {
                  drawBorder: false,
                  display: true,
                  drawOnChartArea: true,
                  drawTicks: false,
                  borderDash: [5, 5]
                },
                ticks: {
                  display: true,
                  padding: 10,
                  color: '#b2b9bf',
                  font: {
                    size: 11,
                    family: "Open Sans",
                    style: 'normal',
                    lineHeight: 2
                  },
                }
              },
              x: {
                grid: {
                  drawBorder: false,
                  display: false,
                  drawOnChartArea: false,
                  drawTicks: false,
                  borderDash: [5, 5]
                },
                ticks: {
                  display: true,
                  color: '#b2b9bf',
                  padding: 20,
                  font: {
                    size: 11,
                    family: "Open Sans",
                    style: 'normal',
                    lineHeight: 2
                  },
                }
              },
            },
          },
        })
    }
}