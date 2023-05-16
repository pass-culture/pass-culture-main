import React from 'react'

import { OFFER_WIZARD_STEP_IDS } from 'components/OfferIndividualBreadcrumb'
import {
  Events,
  OFFER_FORM_NAVIGATION_IN,
  OFFER_FORM_NAVIGATION_MEDIUM,
} from 'core/FirebaseEvents/constants'
import { OFFER_STATUS_DRAFT } from 'core/Offers'
import { Offer, Venue } from 'core/Offers/types'
import { Audience } from 'core/shared'
import useAnalytics from 'hooks/useAnalytics'

import CheckboxCell from './Cells/CheckboxCell'
import IndividualActionsCells from './Cells/IndividualActionsCells'
import OfferNameCell from './Cells/OfferNameCell'
import OfferRemainingStockCell from './Cells/OfferRemainingStockCell'
import OfferStatusCell from './Cells/OfferStatusCell'
import OfferVenueCell from './Cells/OfferVenueCell'
import ThumbCell from './Cells/ThumbCell'

type IndividualOfferItemProps = {
  disabled: boolean
  isSelected: boolean
  offer: Offer
  selectOffer: (offerId: number, selected: boolean, isTemplate: boolean) => void
  editionOfferLink: string
  editionStockLink: string
  venue: Venue
  isOfferEditable: boolean
  refreshOffers: () => void
  audience: Audience
}

const IndividualOfferItem = ({
  disabled,
  offer,
  isSelected,
  selectOffer,
  editionOfferLink,
  editionStockLink,
  venue,
  isOfferEditable,
  refreshOffers,
  audience,
}: IndividualOfferItemProps) => {
  const { logEvent } = useAnalytics()

  const onThumbClick = () => {
    const isDraft = offer.status === OFFER_STATUS_DRAFT
    logEvent?.(Events.CLICKED_OFFER_FORM_NAVIGATION, {
      from: OFFER_FORM_NAVIGATION_IN.OFFERS,
      to: !isDraft
        ? OFFER_WIZARD_STEP_IDS.SUMMARY
        : OFFER_WIZARD_STEP_IDS.INFORMATIONS,
      used: OFFER_FORM_NAVIGATION_MEDIUM.OFFERS_THUMB,
      isEdition: true,
      isDraft: isDraft,
      offerId: offer.id,
    })
  }
  return (
    <>
      <CheckboxCell
        offerId={offer.nonHumanizedId}
        status={offer.status}
        disabled={disabled}
        isSelected={isSelected}
        selectOffer={selectOffer}
        isShowcase={Boolean(offer.isShowcase)}
      />
      <ThumbCell
        offer={offer}
        editionOfferLink={editionOfferLink}
        onThumbClick={onThumbClick}
      />
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
        isOfferEditable={isOfferEditable}
        editionOfferLink={editionOfferLink}
        editionStockLink={editionStockLink}
        refreshOffers={refreshOffers}
      />
    </>
  )
}

export default IndividualOfferItem
