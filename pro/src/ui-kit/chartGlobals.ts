import {
  Chart,
  Filler,
  LinearScale,
  LineController,
  LineElement,
  PointElement,
  TimeSeriesScale,
  Tooltip,
} from 'chart.js'
import 'chartjs-adapter-date-fns'

Chart.register(
  Filler,
  LineController,
  LineElement,
  LinearScale,
  PointElement,
  TimeSeriesScale,
  Tooltip
)
