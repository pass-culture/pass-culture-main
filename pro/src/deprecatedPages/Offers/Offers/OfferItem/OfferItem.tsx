import cn from 'classnames'
import React from 'react'

import { isOfferDisabled, OFFER_STATUS_DRAFT } from 'core/Offers'
import { Offer } from 'core/Offers/types'
import { Audience } from 'core/shared'
import {
  useOfferEditionURL,
  useOfferStockEditionURL,
} from 'hooks/useOfferEditionURL'

import CollectiveOfferItem from './CollectiveOfferItem'
import IndividualOfferItem from './IndividualOfferItem'
import styles from './OfferItem.module.scss'

export type OfferItemProps = {
  disabled?: boolean
  isSelected?: boolean
  offer: Offer
  selectOffer: (offerId: string, selected: boolean, isTemplate: boolean) => void
  audience: Audience
  refreshOffers: () => void
}

const OfferItem = ({
  disabled = false,
  offer,
  isSelected = false,
  selectOffer,
  audience,
  refreshOffers,
}: OfferItemProps) => {
  const { venue, isEducational, isShowcase, status, nonHumanizedId } = offer
  const editionOfferLink = useOfferEditionURL(
    isEducational,
    nonHumanizedId,
    true,
    !!isShowcase,
    status
  )
  const editionStockLink = useOfferStockEditionURL(
    isEducational,
    nonHumanizedId,
    true,
    !!isShowcase
  )

  /* istanbul ignore next: DEBT, TO FIX */
  const isOfferEditable = offer ? offer.isEditable : null
  const isOfferInactiveOrExpiredOrDisabled =
    offer.status == OFFER_STATUS_DRAFT
      ? false
      : !offer.isActive ||
        offer.hasBookingLimitDatetimesPassed ||
        isOfferDisabled(offer.status)

  return (
    <tr
      className={cn(styles['offer-item'], {
        [styles['inactive']]: isOfferInactiveOrExpiredOrDisabled,
      })}
    >
      {audience === Audience.INDIVIDUAL ? (
        <IndividualOfferItem
          disabled={disabled}
          offer={offer}
          isSelected={isSelected}
          selectOffer={selectOffer}
          editionOfferLink={editionOfferLink}
          editionStockLink={editionStockLink}
          venue={venue}
          isOfferEditable={Boolean(isOfferEditable)}
          refreshOffers={refreshOffers}
          audience={audience}
        />
      ) : (
        <CollectiveOfferItem
          disabled={disabled}
          offer={offer}
          isSelected={isSelected}
          selectOffer={selectOffer}
          editionOfferLink={editionOfferLink}
          venue={venue}
          isOfferEditable={Boolean(isOfferEditable)}
          audience={audience}
        />
      )}
    </tr>
  )
}

export default OfferItem
