import moment from 'moment'

export function getDurationFromMinutes(minutes) {
  return minutes >= 60
    ? moment
        .duration(minutes, 'minutes')
        .format('H:mm')
        .replace(':', 'h')
        .replace('00', '')
    : `${minutes}m`
}
