import get from 'lodash.get'

import fp from '../../../../utils/functionnals'

export const filterActivationOffers = offers =>
  offers
    .filter(o => o.id && o)
    .filter(o => o.mediations && o.mediations.length >= 1 && o)
    .filter(
      o => o.event && get(o, 'event.offerType.value') === 'EventType.ACTIVATION'
    )

export const mapActivationOffersToSelectOptions = offers =>
  offers.map(o => {
    const { id: value } = o
    // construction de l'URL de redirection
    const { offerId, id: mediationId } = get(o, 'mediations.0')
    const url = `/decouverte/${offerId}/${mediationId}`
    // construction du label de l'option dans le select
    const venueCity = get(o, 'venue.city')
    const venueName = get(o, 'venue.name')
    const venueCodePostal = get(o, 'venue.postalCode')
    return {
      city: venueCity,
      code: venueCodePostal,
      label: venueName,
      url,
      value,
    }
  })

export const orderActivationOffersByLabel = offers =>
  offers.sort((a, b) => {
    if (a.label > b.label) return 1
    if (a.label < b.label) return -1
    return 0
  })

export const parseActivationOffers = offers =>
  fp.pipe(
    filterActivationOffers,
    mapActivationOffersToSelectOptions,
    orderActivationOffersByLabel
  )(offers)

export const groupOffersByCityCode = offers => {
  let group = offers.reduce((acc, obj) => {
    const { code, city } = obj
    const label = `${code} - ${city}`
    const options = ((acc[code] && acc[code].options) || []).concat([obj])
    return {
      ...acc,
      [code]: { label, options },
    }
  }, {})
  group = Object.keys(group).map(key => ({
    label: group[key].label,
    options: group[key].options,
  }))
  return group
}
