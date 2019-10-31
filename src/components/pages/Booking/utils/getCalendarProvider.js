import moment from 'moment'

const getCalendarProvider = formValues => {
  const isvalid = formValues && formValues.bookables && Array.isArray(formValues.bookables)

  if (!isvalid) return []

  return formValues.bookables
    .filter(o => o && o.beginningDatetime)
    .filter(o => moment.isMoment(o.beginningDatetime))
    .map(o => o.beginningDatetime)
}

export default getCalendarProvider
