import moment from 'moment'

const getCalendarProvider = formValues => {
  const isvalid = formValues && formValues.bookables && Array.isArray(formValues.bookables)

  if (!isvalid) return []

  return formValues.bookables
    .filter(bookable => bookable && bookable.beginningDatetime)
    .filter(bookable => moment.isMoment(bookable.beginningDatetime))
    .map(bookable => bookable.beginningDatetime)
}

export default getCalendarProvider
