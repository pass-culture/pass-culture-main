import React from 'react'

import {
  ListOffersOfferResponseModel,
  ListOffersVenueResponseModel,
} from 'apiClient/v1'
import { Audience } from 'core/shared/types'

import { CheckboxCell } from './Cells/CheckboxCell'
import { IndividualActionsCells } from './Cells/IndividualActionsCell'
import { OfferNameCell } from './Cells/OfferNameCell/OfferNameCell'
import { OfferRemainingStockCell } from './Cells/OfferRemainingStockCell'
import { OfferStatusCell } from './Cells/OfferStatusCell'
import { OfferVenueCell } from './Cells/OfferVenueCell'
import { ThumbCell } from './Cells/ThumbCell'

type IndividualOfferItemProps = {
  disabled: boolean
  isSelected: boolean
  offer: ListOffersOfferResponseModel
  selectOffer: (offerId: number, selected: boolean) => void
  editionOfferLink: string
  editionStockLink: string
  venue: ListOffersVenueResponseModel
  audience: Audience
}

export const IndividualOfferItem = ({
  disabled,
  offer,
  isSelected,
  selectOffer,
  editionOfferLink,
  editionStockLink,
  venue,
  audience,
}: IndividualOfferItemProps) => {
  return (
    <>
      <CheckboxCell
        offerName={offer.name}
        offerId={offer.id}
        status={offer.status}
        disabled={disabled}
        isSelected={isSelected}
        selectOffer={selectOffer}
      />

      <ThumbCell offer={offer} editionOfferLink={editionOfferLink} />

      <OfferNameCell
        offer={offer}
        editionOfferLink={editionOfferLink}
        audience={audience}
      />

      <OfferVenueCell venue={venue} />

      <OfferRemainingStockCell stocks={offer.stocks} />

      <OfferStatusCell status={offer.status} />

      <IndividualActionsCells
        offer={offer}
        editionOfferLink={editionOfferLink}
        editionStockLink={editionStockLink}
      />
    </>
  )
}
