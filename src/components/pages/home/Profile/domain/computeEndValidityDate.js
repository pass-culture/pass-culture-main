import {
  LOCALE_FRANCE,
  MONTH_IN_NUMBER,
  PASS_CULTURE_YEARS_VALIDITY,
  YEAR_IN_NUMBER,
} from '../../../../../utils/date/date'

export const computeEndValidityDate = isoDate => {
  const date = new Date(isoDate)
  const options = {
    ...YEAR_IN_NUMBER,
    ...MONTH_IN_NUMBER,
    day: 'numeric',
  }

  date.setFullYear(date.getFullYear() + PASS_CULTURE_YEARS_VALIDITY)
  return `${date.toLocaleDateString(LOCALE_FRANCE, options)}`
}
