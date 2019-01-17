import get from 'lodash.get'

import fp from '../../../../utils/functionnals'

export const filterActivationOffers = offers =>
  offers
    .filter(o => o.id)
    // filtering mediations
    .filter(({ mediations }) => {
      const filtered =
        (Array.isArray(mediations) && mediations.filter(m => m.id)) || null
      return filtered && filtered.length >= 1
    })
    // filtering venue
    .filter(o => o.venue && o.venue.city && o.venue.name && o.venue.postalCode)
    .filter(
      o => o.event && get(o, 'event.offerType.value') === 'EventType.ACTIVATION'
    )

export const mapActivationOffersToSelectOptions = offers =>
  offers.map(obj => {
    const city = get(obj, 'venue.city')
    const label = get(obj, 'venue.name')
    const code = get(obj, 'venue.postalCode')
    //
    const value = obj.id
    const { id: mediationId } = get(obj, 'mediations.0')
    const url = `/decouverte/${value}/${mediationId}?to=verso`
    return { city, code, label, url, value }
  })

export const orderObjectsByLabel = offers =>
  offers.sort((a, b) => {
    if (a.label > b.label) return 1
    if (a.label < b.label) return -1
    return 0
  })

export const parseActivationOffers = offers =>
  fp.pipe(
    filterActivationOffers,
    mapActivationOffersToSelectOptions,
    orderObjectsByLabel
  )(offers)

export const createOffersGroupWithLabels = offers =>
  offers.reduce((acc, obj) => {
    const { code, city } = obj
    const label = `${code} - ${city}`
    const options = ((acc[code] && acc[code].options) || []).concat([obj])
    return {
      ...acc,
      [code]: { label, options },
    }
  }, {})

export const groupOfferByLabel = group =>
  Object.keys(group).map(key => ({
    label: group[key].label,
    options: group[key].options,
  }))

export const groupOffersByCityCode = offers =>
  fp.pipe(
    createOffersGroupWithLabels,
    groupOfferByLabel,
    orderObjectsByLabel
  )(offers)
