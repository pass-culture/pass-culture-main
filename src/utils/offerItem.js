export function getOfferTypeLabel(event, thing) {
  const offerType = event ? event.offerType : thing.offerType
  return offerType && offerType.label
}
