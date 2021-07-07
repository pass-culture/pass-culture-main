import { GEOLOCATION_CRITERIA } from '../../../components/pages/search/Criteria/criteriaEnums'
import { AppSearchFields } from '../constants'

export const buildGeolocationFilter = params => {
  const { aroundRadius, geolocation, locationType } = params

  if (!geolocation) return []
  if (locationType === GEOLOCATION_CRITERIA.EVERYWHERE) return []
  if (aroundRadius === null) return []

  const center = `${geolocation.latitude}, ${geolocation.longitude}`
  const distance = aroundRadius === 0 ? 1 : aroundRadius
  const unit = aroundRadius === 0 ? 'm' : 'km'
  return [{ [AppSearchFields.venue_position]: { center, distance, unit } }]
}
