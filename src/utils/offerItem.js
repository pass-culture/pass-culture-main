import get from 'lodash.get'

export function getOfferTypeLabel(product) {
  return get(product, 'offerType.label')
}
