import { isGeolocationEnabled, isUserAllowedToSelectCriterion } from '../../../../utils/geolocation'

export const checkUserIsGeolocated = (criterionKey, geolocation, callback) => {
  if (isUserAllowedToSelectCriterion(criterionKey, isGeolocationEnabled(geolocation))) {
    callback(criterionKey)
  }
}
