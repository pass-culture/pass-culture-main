import moment from 'moment/moment'
import 'moment/locale/fr'

const createYears = () => {
  const startYear = 2018
  const currentYear = moment().year()
  let years = []
  for (let i = startYear; i <= currentYear; i++) {
    years.push(i)
  }
  return years
}

const YEAR_OPTIONS = createYears()

export default YEAR_OPTIONS
