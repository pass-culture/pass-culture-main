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

function getNewTargetDateThatPreserveOldHourAndMinutes(newDate, oldDate) {
  const targetMoment = moment(newDate).utc()
  const targetDateHourMinutes = targetMoment.format('HH:mm')

  const [hour, minutes] = targetDateHourMinutes.split(':')

  let triggerMoment = moment(oldDate).utc()

  return triggerMoment
    .hours(hour)
    .minutes(minutes)
    .utc()
    .toISOString()
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
        const shouldNotFillEndDateTimeAtMount =
          Object.keys(prevValues).length === 0

        if (shouldNotFillEndDateTimeAtMount) {
          return {}
        }

        if (!targetDate && !targetTime) {
          return {}
        }

        const nextTargetDate = targetDate ? targetDate : triggerDate
        const updatedTargetDate = getNewTargetDateThatPreserveOldHourAndMinutes(
          nextTargetDate,
          triggerDate
        )

        return {
          [targetDateName]: updatedTargetDate,
        }
      },
    })
)(mapArgsToCacheKey)

export default fillEndDatimeWhenUpdatingBeginningDatetime
