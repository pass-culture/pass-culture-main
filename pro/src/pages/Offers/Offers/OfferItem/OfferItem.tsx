import cn from 'classnames'

import {
  CollectiveOfferResponseModel,
  ListOffersOfferResponseModel,
} from 'apiClient/v1'
import { isOfferEducational } from 'core/OfferEducational/types'
import { OFFER_STATUS_DRAFT } from 'core/Offers/constants'
import { SearchFiltersParams } from 'core/Offers/types'
import { isOfferDisabled } from 'core/Offers/utils/isOfferDisabled'
import { Audience } from 'core/shared/types'
import {
  useOfferEditionURL,
  useOfferStockEditionURL,
} from 'hooks/useOfferEditionURL'

import { CollectiveOfferItem } from './CollectiveOfferItem'
import { IndividualOfferItem } from './IndividualOfferItem'
import styles from './OfferItem.module.scss'

export type OfferItemProps = {
  disabled?: boolean
  isSelected?: boolean
  offer: CollectiveOfferResponseModel | ListOffersOfferResponseModel
  selectOffer: (
    offer: CollectiveOfferResponseModel | ListOffersOfferResponseModel
  ) => void
  audience: Audience
  urlSearchFilters: SearchFiltersParams
}

export const OfferItem = ({
  disabled = false,
  offer,
  isSelected = false,
  selectOffer,
  audience,
  urlSearchFilters,
}: OfferItemProps) => {
  const { venue, isEducational, isShowcase, status, id } = offer
  const editionOfferLink = useOfferEditionURL(
    isEducational,
    id,
    !!isShowcase,
    status
  )
  const editionStockLink = useOfferStockEditionURL(
    isEducational,
    id,
    !!isShowcase
  )

  const isOfferInactiveOrExpiredOrDisabled =
    offer.status === OFFER_STATUS_DRAFT
      ? false
      : !offer.isActive ||
        offer.hasBookingLimitDatetimesPassed ||
        isOfferDisabled(offer.status)

  return (
    <tr
      className={cn(styles['offer-item'], {
        [styles['inactive']]: isOfferInactiveOrExpiredOrDisabled,
      })}
      data-testid="offer-item-row"
    >
      {/* TODO the audience prop could probably be removed in the future */}
      {/* as it is redundant with the offer.isEducational property */}
      {audience === Audience.INDIVIDUAL && !isOfferEducational(offer) && (
        <IndividualOfferItem
          disabled={disabled}
          offer={offer}
          isSelected={isSelected}
          selectOffer={selectOffer}
          editionOfferLink={editionOfferLink}
          editionStockLink={editionStockLink}
          venue={venue}
          audience={audience}
        />
      )}
      {audience === Audience.COLLECTIVE && isOfferEducational(offer) && (
        <CollectiveOfferItem
          disabled={disabled}
          offer={offer}
          isSelected={isSelected}
          selectOffer={selectOffer}
          editionOfferLink={editionOfferLink}
          venue={venue}
          audience={audience}
          urlSearchFilters={urlSearchFilters}
        />
      )}
    </tr>
  )
}
