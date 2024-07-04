import React from 'react'

import {
  CollectiveOfferResponseModel,
  ListOffersVenueResponseModel,
} from 'apiClient/v1'
import { SearchFiltersParams } from 'core/Offers/types'
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
  selectOffer: (offer: CollectiveOfferResponseModel) => void
  editionOfferLink: string
  venue: ListOffersVenueResponseModel
  audience: Audience
  urlSearchFilters: SearchFiltersParams
}

export const CollectiveOfferItem = ({
  disabled,
  offer,
  isSelected,
  selectOffer,
  editionOfferLink,
  venue,
  audience,
  urlSearchFilters,
}: CollectiveOfferItemProps) => {
  return (
    <>
      <CheckboxCell
        offerName={offer.name}
        status={offer.status}
        disabled={disabled}
        isSelected={isSelected}
        selectOffer={() => selectOffer(offer)}
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
        urlSearchFilters={urlSearchFilters}
      />
    </>
  )
}
