import moment from 'moment'
import isEmpty from '../strings/isEmpty'
import isString from '../strings/isString'

export const humanizeBeginningDateTime = () => items => {
  const format = 'dddd DD/MM/YYYY à HH:mm'
  return items.map(obj => {
    let date = obj.beginningDatetime || null
    const ismoment = date && moment.isMoment(date)
    const isstring = date && isString(date) && !isEmpty(date)
    const isvaliddate = isstring && moment(date, moment.ISO_8601, true).isValid()
    const isvalid = isvaliddate || ismoment
    if (!isvalid) return obj
    if (isstring) date = moment(date)
    const humanBeginningDate = date.format(format)
    return Object.assign({}, obj, { humanBeginningDate })
  })
}
