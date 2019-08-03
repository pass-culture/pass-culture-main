import moment from 'moment'

const getDurationFromMinutes = minutes => {
  return minutes >= 60
    ? moment
        .duration(minutes, 'minutes')
        .format('H:mm')
        .replace(':', 'h')
        .replace('00', '')
    : `${minutes}m`
}

export default getDurationFromMinutes
