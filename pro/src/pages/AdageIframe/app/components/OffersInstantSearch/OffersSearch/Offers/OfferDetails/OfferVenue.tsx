import { CollectiveOfferOfferVenue, OfferAddressType } from '@/apiClient/adage'

interface OfferVenueProps {
  offerVenue: CollectiveOfferOfferVenue
}

export const OfferVenue = ({ offerVenue }: OfferVenueProps): JSX.Element => {
  if (offerVenue.addressType === OfferAddressType.OTHER) {
    return <div>{offerVenue.otherAddress}</div>
  }
  if (offerVenue.addressType === OfferAddressType.SCHOOL) {
    return <div>Dans l’établissement scolaire</div>
  }

  return (
    <div>
      <div>{offerVenue.publicName || offerVenue.name}</div>
      <div>
        {offerVenue.address}, {offerVenue.postalCode} {offerVenue.city}
      </div>
    </div>
  )
}
