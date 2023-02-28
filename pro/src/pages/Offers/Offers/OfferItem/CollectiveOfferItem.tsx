import React from 'react'

import { OfferStatus } from 'apiClient/v1'
import { Offer, Venue } from 'core/Offers/types'
import { Audience } from 'core/shared'

import BookingLinkCell from './Cells/BookingLinkCell'
import CheckboxCell from './Cells/CheckboxCell'
import CollectiveOfferStatusCell from './Cells/CollectiveOfferStatusCell'
import DuplicateOfferCell from './Cells/DuplicateOfferCell'
import EditOfferCell from './Cells/EditOfferCell'
import OfferInstitutionCell from './Cells/OfferInstitutionCell'
import OfferNameCell from './Cells/OfferNameCell'
import OfferVenueCell from './Cells/OfferVenueCell'
import ThumbCell from './Cells/ThumbCell'

export type CollectiveOfferItemProps = {
  disabled: boolean
  isSelected: boolean
  offer: Offer
  selectOffer: (offerId: string, selected: boolean, isTemplate: boolean) => void
  editionOfferLink: string
  venue: Venue
  isOfferEditable: boolean
  audience: Audience
}

const CollectiveOfferItem = ({
  disabled,
  offer,
  isSelected,
  selectOffer,
  editionOfferLink,
  venue,
  isOfferEditable,
  audience,
}: CollectiveOfferItemProps) => {
  return (
    <>
      <CheckboxCell
        offerId={offer.id}
        status={offer.status}
        disabled={disabled}
        isSelected={isSelected}
        selectOffer={selectOffer}
        isShowcase={Boolean(offer.isShowcase)}
      />
      <ThumbCell offer={offer} editionOfferLink={editionOfferLink} />
      <OfferNameCell
        offer={offer}
        editionOfferLink={editionOfferLink}
        audience={audience}
      />
      <OfferVenueCell venue={venue} />
      <OfferInstitutionCell
        educationalInstitution={offer.educationalInstitution}
      />

      <CollectiveOfferStatusCell offer={offer} />

      {Boolean(offer.isShowcase) && (
        <DuplicateOfferCell templateOfferId={offer.id} />
      )}

      {(offer.status == OfferStatus.SOLD_OUT ||
        offer.status == OfferStatus.EXPIRED) &&
        offer.educationalBooking && (
          <BookingLinkCell
            bookingId={offer.educationalBooking?.id}
            bookingStatus={offer.educationalBooking.booking_status}
            offerEventDate={offer.stocks[0].beginningDatetime}
          />
        )}
      {offer.isEditable && !offer.isPublicApi && (
        <EditOfferCell
          offer={offer}
          isOfferEditable={isOfferEditable}
          editionOfferLink={editionOfferLink}
        />
      )}
    </>
  )
}

export default CollectiveOfferItem
