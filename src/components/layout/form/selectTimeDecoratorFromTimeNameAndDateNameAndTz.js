import moment from 'moment'
import createDecorator from 'final-form-calculate'
import createCachedSelector from 're-reselect'

function mapArgsToCacheKey(timeName, dateName, tz) {
  return `${timeName || ''}${dateName || ''}${tz || ''}`
}

export const selectTimeDecoratorFromTimeNameAndDateNameAndTz = createCachedSelector(
  timeName => timeName,
  (timeName, dateName) => dateName,
  (timeName, dateName, tz) => tz,
  (timeName, dateName, tz) =>
    createDecorator(
      {
        field: timeName,
        updates: (time, timeName, allValues) => {
          if (!time) {
            return {}
          }
          const [hour, minutes] = time.split(':')
          const previousDate = moment(allValues[dateName])
          const updatedDate = previousDate
            .tz(tz)
            .hours(hour)
            .minutes(minutes)
            .toISOString()
          return {
            [dateName]: updatedDate,
          }
        },
      },
      {
        field: dateName,
        updates: date => {
          const updatedTime = moment(date)
            .tz(tz)
            .format('HH:mm')
          return {
            [timeName]: updatedTime,
          }
        },
      }
    )
)(mapArgsToCacheKey)

export default selectTimeDecoratorFromTimeNameAndDateNameAndTz
