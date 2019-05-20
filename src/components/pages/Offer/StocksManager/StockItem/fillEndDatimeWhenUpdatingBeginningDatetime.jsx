import createDecorator from 'final-form-calculate'
import moment from 'moment'
import 'moment-timezone'
import createCachedSelector from 're-reselect'

function mapArgsToCacheKey({
  triggerDateName,
  targetDateName,
  targetTimeName,
  timezone,
}) {
  return `${triggerDateName || ''}${targetDateName || ''}${targetTimeName ||
    ''}${timezone || ''}`
}

export const fillEndDatimeWhenUpdatingBeginningDatetime = createCachedSelector(
  ({ triggerDateName }) => triggerDateName,
  ({ targetDateName }) => targetDateName,
  ({ targetTimeName }) => targetTimeName,
  ({ timezone }) => timezone,
  (triggerDateName, targetDateName, targetTimeName, timezone) =>
    createDecorator({
      field: triggerDateName,
      updates: (triggerDate, doublonTriggerDateName, allValues) => {
        const targetDate = allValues[targetDateName]
        const targetTime = allValues[targetTimeName]
        let nextTargetDate = targetDate

        if (!targetDate) {
          if (!targetTime) {
            return {}
          }
          nextTargetDate = triggerDate
        }
        let targetMoment = moment(nextTargetDate).utc()
        const targetDateHourMinutes = targetMoment.format('HH:mm')
        const [hour, minutes] = targetDateHourMinutes.split(':')

        let triggerMoment = moment(triggerDate).utc()
        const updatedTargetDate = triggerMoment
          .hours(hour)
          .minutes(minutes)
          .toISOString()

        return {
          [targetDateName]: updatedTargetDate,
        }
      },
    })
)(mapArgsToCacheKey)

export default fillEndDatimeWhenUpdatingBeginningDatetime
