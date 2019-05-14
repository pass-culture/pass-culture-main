import createDecorator from 'final-form-calculate'
import moment from 'moment'
import 'moment-timezone'
import createCachedSelector from 're-reselect'

function mapArgsToCacheKey({ dateName, hours, minutes, timezone }) {
  return `${dateName || ''}${hours || ''}${minutes || ''}${timezone || ''}`
}

const forceDateAtSpecificHoursAndMinutes = createCachedSelector(
  ({ dateName }) => dateName,
  ({ hours }) => hours,
  ({ minutes }) => minutes,
  ({ timezone }) => timezone,
  (dateName, hours, minutes, timezone) =>
    createDecorator({
      field: dateName,
      updates: async date => {
        let dateMoment = moment(date).utc()
        if (timezone) {
          dateMoment = dateMoment.tz(timezone)
        }

        const updatedDate = dateMoment
          .hours(hours)
          .minutes(minutes)
          .toISOString()

        return {
          [dateName]: updatedDate,
        }
      },
    })
)(mapArgsToCacheKey)

export default forceDateAtSpecificHoursAndMinutes
