import moment from 'moment'
import { isSameDayInEachTimezone, getDisplayPrice } from '../../../helpers'

const parseHoursByStockId = (allFormValues, format = 'HH:mm') => {
  const isvalid =
    allFormValues &&
    allFormValues.bookables &&
    Array.isArray(allFormValues.bookables) &&
    allFormValues.bookables.length > 0 &&
    allFormValues.date &&
    allFormValues.date.date &&
    moment.isMoment(allFormValues.date.date)
  if (!isvalid) return []
  const { date, bookables } = allFormValues
  return bookables
    .filter(o => o.id && typeof o.id === 'string')
    .filter(o => moment.isMoment(o.beginningDatetime))
    .filter(o => isSameDayInEachTimezone(date.date, o.beginningDatetime))
    .map(obj => {
      // parse les infos d'une offre
      // pour être affichée dans la selectbox
      const time = obj.beginningDatetime.format(format)
      const devised = getDisplayPrice(obj.price)
      const label = `${time} - ${devised}`
      return { id: obj.id, label }
    })
}

export default parseHoursByStockId
