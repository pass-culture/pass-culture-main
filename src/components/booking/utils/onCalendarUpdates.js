import moment from 'moment'
import { isSameDayInEachTimezone } from '../../../helpers'

/**
 * Calcule les valeurs du form
 * En fonction de la date selectionnée par l'user
 *
 * NOTE -> Howto implement calculator: https://codesandbox.io/s/oq52p6v96y
 * FIXME -> hot-reload cause console.error
 */
const onCalendarUpdates = (selectedDate, name, allFormValues) => {
  if (!allFormValues) throw new Error('Missing arguments form values')
  if (!selectedDate) return allFormValues
  const resetObj = { price: null, stockId: null, time: null }
  const isvalid = selectedDate.date && moment.isMoment(selectedDate.date)
  if (!isvalid) return resetObj
  // iteration sur l'array bookables
  // recupere le premier event pour la selection par l'user
  const { bookables } = allFormValues
  const filtered =
    bookables &&
    Array.isArray(bookables) &&
    bookables.length &&
    bookables
      .filter(o => o && o.beginningDatetime && moment.isMoment(o.beginningDatetime))
      .find(o => isSameDayInEachTimezone(selectedDate.date, o.beginningDatetime))
  if (!filtered) return resetObj
  return {
    price: filtered.price,
    stockId: filtered.id,
    time: filtered.id,
  }
}

export default onCalendarUpdates
