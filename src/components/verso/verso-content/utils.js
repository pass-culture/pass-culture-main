import moment from 'moment'

export function getWhatTitleFromLabelAndIsVirtualVenue(label, isVirtualVenue) {
  if (!label) {
    return ''
  }
  if (label.includes('(sur supports physiques ou en ligne)')) {
    return isVirtualVenue
      ? label.replace('sur supports physiques ou ', '')
      : label.replace(' ou en ligne', '')
  }
  return label
}

export function getDurationFromMinutes(minutes) {
  return minutes >= 60
    ? moment
        .duration(minutes, 'minutes')
        .format('H:mm')
        .replace(':', 'h')
        .replace('00', '')
    : minutes
}
