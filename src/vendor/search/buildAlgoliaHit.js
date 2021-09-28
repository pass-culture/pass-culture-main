import { AppSearchFields, TRUE } from './constants'

// TODO(antoinewg) We need this function temporarily but delete when we migrate completely to App Search
export const buildAlgoliaHit = searchHit => {
  const dates = searchHit.getRaw(AppSearchFields.dates).map(ts => new Date(ts).getTime() / 1000)
  const prices = searchHit.getRaw(AppSearchFields.prices).map(p => +p / 100)
  const priceMax = Math.max(...prices)
  const priceMin = Math.min(...prices)

  const geoloc = searchHit.getRaw(AppSearchFields.venue_position)
  const [lat, lng] = (geoloc || ',').split(',')

  // Offers are stored in engines grouped by a meta-engine. Thus their ids are `offers-2|9234`.
  const id = searchHit.getRaw(AppSearchFields.id)
  const objectID = id.split('|').slice(-1)[0]

  return {
    offer: {
      dates,
      isDigital: +searchHit.getRaw(AppSearchFields.is_digital) === TRUE,
      isDuo: +searchHit.getRaw(AppSearchFields.is_duo) === TRUE,
      isEvent: +searchHit.getRaw(AppSearchFields.is_event) === TRUE,
      label: searchHit.getRaw(AppSearchFields.label),
      name: searchHit.getRaw(AppSearchFields.name),
      priceMax,
      priceMin,
      thumbUrl: searchHit.getRaw(AppSearchFields.thumb_url),
    },
    _geoloc: {
      lat: isNaN(parseFloat(lat)) ? null : parseFloat(lat),
      lng: isNaN(parseFloat(lng)) ? null : parseFloat(lng),
    },
    venue: {
      departmentCode: searchHit.getRaw(AppSearchFields.venue_department_code),
      name: searchHit.getRaw(AppSearchFields.venue_name),
      publicName: searchHit.getRaw(AppSearchFields.venue_public_name),
    },
    objectID,
  }
}
