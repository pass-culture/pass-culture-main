import React from 'react'

import {
  CollectiveOfferResponseModel,
  ListOffersVenueResponseModel,
} from 'apiClient/v1'
import { Audience } from 'core/shared/types'

import { CheckboxCell } from './Cells/CheckboxCell'
import { CollectiveActionsCells } from './Cells/CollectiveActionsCells'
import { CollectiveOfferStatusCell } from './Cells/CollectiveOfferStatusCell/CollectiveOfferStatusCell'
import { OfferInstitutionCell } from './Cells/OfferInstitutionCell'
import { OfferNameCell } from './Cells/OfferNameCell/OfferNameCell'
import { OfferVenueCell } from './Cells/OfferVenueCell'
import { ThumbCell } from './Cells/ThumbCell'

type CollectiveOfferItemProps = {
  disabled: boolean
  isSelected: boolean
  offer: CollectiveOfferResponseModel
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
        offer={offer}
        editionOfferLink={editionOfferLink}
      />
    </>
  )
}
