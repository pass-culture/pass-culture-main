export const MONTH_OPTIONS = [
  'janvier',
  'février',
  'mars',
  'avril',
  'mai',
  'juin',
  'juillet',
  'août',
  'septembre',
  'ocotbre',
  'novembre',
  'décembre',
]

const createYearArray = () => {
  const startYear = 2018
  let currentYear = new Date().getFullYear()
  let years = []
  for (let i = startYear; i <= currentYear; i++) {
    years.push(i)
  }
  return years
}

export const YEAR_OPTIONS = createYearArray()
