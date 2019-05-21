import createDecorator from 'final-form-calculate'
import moment from 'moment'
import 'moment-timezone'
import createCachedSelector from 're-reselect'

function mapArgsToCacheKey({
  triggerDateName,
  targetDateName,
  targetTimeName,
}) {
  return `${triggerDateName || ''}${targetDateName || ''}${targetTimeName ||
    ''}`
}

export const fillEndDatimeWhenUpdatingBeginningDatetime = createCachedSelector(
  ({ triggerDateName }) => triggerDateName,
  ({ targetDateName }) => targetDateName,
  ({ targetTimeName }) => targetTimeName,
  (triggerDateName, targetDateName, targetTimeName) =>
    createDecorator({
      field: triggerDateName,
      updates: (triggerDate, doublonTriggerDateName, allValues, prevValues) => {
        const targetDate = allValues[targetDateName]
        const targetTime = allValues[targetTimeName]
        let nextTargetDate = targetDate

        const shouldNotFillEndDateTimeAtMount =
          Object.keys(prevValues).length === 0
        if (shouldNotFillEndDateTimeAtMount) {
          return {}
        }

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
          .utc()
          .toISOString()

        return {
          [targetDateName]: updatedTargetDate,
        }
      },
    })
)(mapArgsToCacheKey)

export default fillEndDatimeWhenUpdatingBeginningDatetime
