import classNames from 'classnames'

import { ListOffersOfferResponseModel } from 'apiClient/v1'
import { OFFER_STATUS_DRAFT } from 'core/Offers/constants'
import { isOfferDisabled } from 'core/Offers/utils/isOfferDisabled'
import { useActiveFeature } from 'hooks/useActiveFeature'
import {
  useOfferEditionURL,
  useOfferStockEditionURL,
} from 'hooks/useOfferEditionURL'

import { AddressCell } from '../../Cells/AddressCell'
import { CheckboxCell } from '../../Cells/CheckboxCell'
import { IndividualActionsCells } from '../../Cells/IndividualActionsCell'
import { OfferNameCell } from '../../Cells/OfferNameCell/OfferNameCell'
import { OfferRemainingStockCell } from '../../Cells/OfferRemainingStockCell'
import { OfferStatusCell } from '../../Cells/OfferStatusCell'
import { OfferVenueCell } from '../../Cells/OfferVenueCell'
import { ThumbCell } from '../../Cells/ThumbCell'

import styles from './IndividualOfferRow.module.scss'

export type IndividualOfferRowProps = {
  isSelected: boolean
  offer: ListOffersOfferResponseModel
  selectOffer: (offer: ListOffersOfferResponseModel) => void
}

export const IndividualOfferRow = ({
  offer,
  isSelected,
  selectOffer,
}: IndividualOfferRowProps) => {
  const isSplitOfferEnabled = useActiveFeature('WIP_SPLIT_OFFER')
  const offerAddressEnabled = useActiveFeature('WIP_ENABLE_OFFER_ADDRESS')

  const editionOfferLink = useOfferEditionURL({
    isOfferEducational: false,
    offerId: offer.id,
    isShowcase: false,
    status: offer.status,
    isSplitOfferEnabled,
  })
  const editionStockLink = useOfferStockEditionURL(false, offer.id, false)

  const isOfferInactiveOrExpiredOrDisabled =
    offer.status === OFFER_STATUS_DRAFT
      ? false
      : !offer.isActive ||
        offer.hasBookingLimitDatetimesPassed ||
        isOfferDisabled(offer.status)

  return (
    <tr
      className={classNames(styles['individual-row'], {
        [styles['inactive']]: isOfferInactiveOrExpiredOrDisabled,
      })}
      data-testid="offer-item-row"
    >
      <CheckboxCell
        offerName={offer.name}
        isSelected={isSelected}
        disabled={isOfferDisabled(offer.status)}
        selectOffer={() => selectOffer(offer)}
      />

      <ThumbCell offer={offer} editionOfferLink={editionOfferLink} />

      <OfferNameCell offer={offer} editionOfferLink={editionOfferLink} />

      {offerAddressEnabled && offer.address ? (
        <AddressCell address={offer.address} />
      ) : (
        <OfferVenueCell venue={offer.venue} />
      )}

      <OfferRemainingStockCell stocks={offer.stocks} />

      <OfferStatusCell status={offer.status} />

      <IndividualActionsCells
        offer={offer}
        editionOfferLink={editionOfferLink}
        editionStockLink={editionStockLink}
      />
    </tr>
  )
}
