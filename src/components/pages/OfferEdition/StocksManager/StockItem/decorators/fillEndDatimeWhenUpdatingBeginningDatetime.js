import createDecorator from 'final-form-calculate'
import moment from 'moment'
import 'moment-timezone'
import createCachedSelector from 're-reselect'

function mapArgsToCacheKey({ triggerDateName, targetDateName, targetTimeName, timezone }) {
  return `${triggerDateName || ''}${targetDateName || ''}${targetTimeName || ''}${timezone || ''}`
}

const getNewTargetDateThatPreserveOldHourAndMinutes = (newDate, oldDate, timezone) => {
  const targetMoment = moment(newDate).utc()
  const targetDateHourMinutes = targetMoment.format('HH:mm')

  const [hour, minutes] = targetDateHourMinutes.split(':')

  let triggerMoment = moment(oldDate).utc()
  if (timezone) {
    triggerMoment = triggerMoment.tz(timezone)
  }

  return triggerMoment
    .hours(hour)
    .minutes(minutes)
    .utc()
    .toISOString()
}

export const updateEndDateTimeField = (
  triggerDate,
  doublonTriggerDateName,
  allValues,
  prevValues,
  targetDateName,
  targetTimeName,
  timezone
) => {
  const targetDate = allValues[targetDateName]
  const targetTime = allValues[targetTimeName]
  const shouldNotFillEndDateTimeAtMount = Object.keys(prevValues).length === 0

  if (shouldNotFillEndDateTimeAtMount) {
    return {}
  }

  if (!targetDate && !targetTime) {
    return {}
  }

  const nextTargetDate = targetDate ? targetDate : triggerDate
  const updatedTargetDate = getNewTargetDateThatPreserveOldHourAndMinutes(
    nextTargetDate,
    triggerDate,
    timezone
  )

  return {
    [targetDateName]: updatedTargetDate,
  }
}

const fillEndDatimeWhenUpdatingBeginningDatetime = createCachedSelector(
  ({ triggerDateName }) => triggerDateName,
  ({ targetDateName }) => targetDateName,
  ({ targetTimeName }) => targetTimeName,
  ({ timezone }) => timezone,
  (triggerDateName, targetDateName, targetTimeName, timezone) =>
    createDecorator({
      field: triggerDateName,
      updates: (triggerDate, doublonTriggerDateName, allValues, prevValues) =>
        updateEndDateTimeField(
          triggerDate,
          doublonTriggerDateName,
          allValues,
          prevValues,
          targetDateName,
          targetTimeName,
          timezone
        ),
    })
)(mapArgsToCacheKey)

export default fillEndDatimeWhenUpdatingBeginningDatetime
