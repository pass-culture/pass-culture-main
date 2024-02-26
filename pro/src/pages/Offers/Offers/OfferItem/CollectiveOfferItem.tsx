import React from 'react'

import { ListOffersVenueResponseModel } from 'apiClient/v1'
import { Offer } from 'core/Offers/types'
import { Audience } from 'core/shared'

import CheckboxCell from './Cells/CheckboxCell'
import CollectiveActionsCells from './Cells/CollectiveActionsCells'
import CollectiveOfferStatusCell from './Cells/CollectiveOfferStatusCell'
import OfferInstitutionCell from './Cells/OfferInstitutionCell'
import OfferNameCell from './Cells/OfferNameCell'
import OfferVenueCell from './Cells/OfferVenueCell'
import ThumbCell from './Cells/ThumbCell'

type CollectiveOfferItemProps = {
  disabled: boolean
  isSelected: boolean
  offer: Offer
  selectOffer: (offerId: number, selected: boolean, isTemplate: boolean) => void
  editionOfferLink: string
  venue: ListOffersVenueResponseModel
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
        offerName={offer.name}
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
      <CollectiveActionsCells
        offer={offer}
        isOfferEditable={isOfferEditable}
        editionOfferLink={editionOfferLink}
      />
    </>
  )
}

export default CollectiveOfferItem
