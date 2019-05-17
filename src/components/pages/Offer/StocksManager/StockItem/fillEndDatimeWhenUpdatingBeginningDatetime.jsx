import createDecorator from 'final-form-calculate'
import moment from 'moment'
import 'moment-timezone'
import createCachedSelector from 're-reselect'

function mapArgsToCacheKey(triggerDateName, targetDateName, timezone) {
  return `${triggerDateName || ''}${targetDateName || ''}${timezone || ''}`
}

export const fillEndDatimeWhenUpdatingBeginningDatetime = createCachedSelector(
  triggerDateName => triggerDateName,
  (triggerDateName, targetDateName) => targetDateName,
  (triggerDateName, targetDateName, targetTimeName, timezone) => targetTimeName,
  (triggerqDateName, targetDateName, targetTimeName, timezone) => timezone,
  (triggerDateName, targetDateName, targetTimeName, timezone) =>
    createDecorator({
      field: triggerDateName,
      updates: (triggerDate, doublonTriggerDateName, allValues) => {
        const targetDate = allValues[targetDateName]
        const targetTime = allValues[targetTimeName]
        let nextTargetDate = targetDate

        console.log('targetDate  :', targetDate)
        if (!targetDate) {
          // if (!targetTime) {
          return {}
          // }
          nextTargetDate = triggerDate
        }

        let targetMoment = moment(nextTargetDate).utc()
        if (timezone) {
          targetMoment = targetMoment.tz(timezone)
        }

        const targetDateHourMinutes = targetMoment.format('HH:mm')
        const [hour, minutes] = targetDateHourMinutes.split(':')

        let triggerMoment = moment(triggerDate).utc()
        if (timezone) {
          triggerMoment = triggerMoment.tz(timezone)
        }

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
