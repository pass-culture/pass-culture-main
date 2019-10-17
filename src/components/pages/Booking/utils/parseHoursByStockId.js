import moment from 'moment'
import getDisplayPrice from '../../../../helpers/getDisplayPrice'
import isSameDayInEachTimezone from '../../../../helpers/isSameDayInEachTimezone'

const parseHoursByStockId = (allFormValues, format = 'HH:mm') => {
  const hasBookableDates =
    allFormValues &&
    allFormValues.bookables &&
    Array.isArray(allFormValues.bookables) &&
    allFormValues.bookables.length > 0 &&
    allFormValues.date &&
    moment.isMoment(allFormValues.date)

  if (!hasBookableDates) return []
  const { date, bookables } = allFormValues

  return bookables
    .filter(o => o.id && typeof o.id === 'string')
    .filter(o => moment.isMoment(o.beginningDatetime))
    .filter(o => isSameDayInEachTimezone(date, o.beginningDatetime))
    .map(obj => {
      const time = obj.beginningDatetime.format(format)
      const devised = getDisplayPrice(obj.price)
      const label = `${time} - ${devised}`
      return { id: obj.id, label }
    })
}

export default parseHoursByStockId
