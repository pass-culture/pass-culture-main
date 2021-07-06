import { AppSearchFields, TRUE } from './constants'

// TODO(antoinewg) We need this function temporarily but delete when we migrate completely to App Search
export const buildAlgoliaHit = searchHit => {
  const dates = searchHit.getRaw(AppSearchFields.dates).map(ts => +ts)
  const prices = searchHit.getRaw(AppSearchFields.prices).map(p => +p / 100)
  const geoloc = searchHit.getRaw(AppSearchFields.venue_position)
  const [lat, lng] = (geoloc || ',').split(',')

  return {
    offer: {
      category: searchHit.getRaw(AppSearchFields.category),
      dates,
      description: searchHit.getRaw(AppSearchFields.description),
      isDigital: +searchHit.getRaw(AppSearchFields.is_digital) === TRUE,
      isDuo: +searchHit.getRaw(AppSearchFields.is_duo) === TRUE,
      name: searchHit.getRaw(AppSearchFields.name),
      prices,
      thumbUrl: searchHit.getRaw(AppSearchFields.thumb_url),
    },
    _geoloc: {
      lat: isNaN(parseFloat(lat)) ? null : parseFloat(lat),
      lng: isNaN(parseFloat(lng)) ? null : parseFloat(lng),
    },
    objectID: searchHit.getRaw(AppSearchFields.id),
  }
}
