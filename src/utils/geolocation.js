import { MOBILE_OS } from '../utils/config'

export function distanceInMeters(lat1, lon1, lat2, lon2) {
  var EARTH_RADIUS_KM = 6378.137
  var dLat = lat2 * Math.PI / 180 - lat1 * Math.PI / 180
  var dLon = lon2 * Math.PI / 180 - lon1 * Math.PI / 180
  var a =
    Math.sin(dLat / 2) * Math.sin(dLat / 2) +
    +Math.cos(lat1 * Math.PI / 180) *
      Math.cos(lat2 * Math.PI / 180) *
      Math.sin(dLon / 2) *
      Math.sin(dLon / 2)
  var c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a))
  var d = EARTH_RADIUS_KM * c
  return d * 1000
}

export function navigationLink(lat, long) {
  //see https://stackoverflow.com/questions/9688607/how-to-open-a-mobile-devices-map-app-when-a-user-clicks-on-a-link
  if (MOBILE_OS === 'ios') {
    return (
      'maps://maps.google.com/maps?daddr=' + lat + ',' + long
    )
  } else if (MOBILE_OS === 'android') {
    return (
      'http://maps.google.com/maps?daddr=' + lat + ',' + long
    )
  } else {
    return 'https://www.openstreetmap.org/#map=18/' + lat + '/' + long
  }
}
