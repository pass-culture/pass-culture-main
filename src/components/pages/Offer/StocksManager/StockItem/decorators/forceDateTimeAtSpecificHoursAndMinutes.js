import createDecorator from 'final-form-calculate'
import moment from 'moment'
import 'moment-timezone'
import createCachedSelector from 're-reselect'

function mapArgsToCacheKey({ dateTimeName, hours, minutes, timezone }) {
  return `${dateTimeName || ''}${hours || ''}${minutes || ''}${timezone || ''}`
}

const forceDateTimeAtSpecificHoursAndMinutes = createCachedSelector(
  ({ dateTimeName }) => dateTimeName,
  ({ hours }) => hours,
  ({ minutes }) => minutes,
  ({ timezone }) => timezone,
  (dateTimeName, hours, minutes, timezone) =>
    createDecorator({
      field: dateTimeName,
      updates: async date => {
        let dateTimeMoment = moment(date).utc()
        if (timezone) {
          dateTimeMoment = dateTimeMoment.tz(timezone)
        }

        const updatedDateTime = dateTimeMoment
          .hours(hours)
          .minutes(minutes)
          .toISOString()

        return {
          [dateTimeName]: updatedDateTime,
        }
      },
    })
)(mapArgsToCacheKey)

export default forceDateTimeAtSpecificHoursAndMinutes
