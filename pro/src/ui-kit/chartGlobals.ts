import { Chart } from 'chart.js/auto'

import 'chartjs-adapter-date-fns'
import { FORMAT_DD_MM_YYYY } from 'utils/date'

export const chartColors = {
  primary: '#870087',
  black: '#151515',
}

// We have only one chart for now so I put here all the options that I think
// should be defaults but we can adapt these defaults when we add more charts
Chart.defaults.locale = 'fr-FR'
Chart.defaults.font.family = 'Montserrat-Regular'
Chart.defaults.maintainAspectRatio = false

Chart.defaults.scales.time.time.displayFormats = {
  day: FORMAT_DD_MM_YYYY,
  month: 'MMMM',
}
Chart.defaults.scales.time.time.minUnit = 'day'
Chart.defaults.scales.time.ticks.font = { weight: 600 }
Chart.defaults.scales.time.ticks.color = chartColors.black
Chart.defaults.scales.time.time.tooltipFormat = FORMAT_DD_MM_YYYY
Chart.defaults.scales.time.grid = { drawTicks: false }

Chart.defaults.scales.linear.ticks.font = { weight: 600 }
Chart.defaults.scales.linear.ticks.color = chartColors.black
Chart.defaults.scales.linear.grid = { drawTicks: false }

Chart.defaults.plugins.legend.display = false
