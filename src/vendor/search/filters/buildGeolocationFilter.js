import { AppSearchFields } from '../constants'

export const buildGeolocationFilter = params => {
  const { aroundRadius, geolocation, searchAround } = params

  if (!geolocation) return []
  const { latitude, longitude } = geolocation
  if (!latitude || !longitude) return []

  if (!searchAround || aroundRadius === null) return []

  const center = `${geolocation.latitude}, ${geolocation.longitude}`
  const distance = aroundRadius === 0 ? 1 : aroundRadius
  const unit = aroundRadius === 0 ? 'm' : 'km'
  return [{ [AppSearchFields.venue_position]: { center, distance, unit } }]
}
