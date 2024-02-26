import React from 'react'

import {
  CollectiveOfferResponseModel,
  ListOffersVenueResponseModel,
} from 'apiClient/v1'
import { Offer } from 'core/Offers/types'
import { Audience } from 'core/shared'

import CheckboxCell from './Cells/CheckboxCell'
import { CollectiveActionsCells } from './Cells/CollectiveActionsCells/CollectiveActionsCells'
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
  audience: Audience
}

export const CollectiveOfferItem = ({
  disabled,
  offer,
  isSelected,
  selectOffer,
  editionOfferLink,
  venue,
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
        // TODO offerCustomType
        // This "as" is temporary while unwrapping the Offer custom type
        // this function is only used in the case where Offer = ListOffersOfferResponseModel
        // when the Offer type is fully unwrapped, this "as" will be removed
        offer={offer as CollectiveOfferResponseModel}
        editionOfferLink={editionOfferLink}
      />
    </>
  )
}
