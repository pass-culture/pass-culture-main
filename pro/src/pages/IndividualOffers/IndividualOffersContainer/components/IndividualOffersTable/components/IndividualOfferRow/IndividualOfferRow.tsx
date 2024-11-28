import classNames from 'classnames'

import { ListOffersOfferResponseModel } from 'apiClient/v1'
import { OFFER_STATUS_DRAFT } from 'commons/core/Offers/constants'
import { isOfferDisabled } from 'commons/core/Offers/utils/isOfferDisabled'
import { useActiveFeature } from 'commons/hooks/useActiveFeature'
import {
  useOfferEditionURL,
  useOfferStockEditionURL,
} from 'commons/hooks/useOfferEditionURL'
import { CheckboxCell } from 'components/OffersTable/Cells/CheckboxCell'
import { OfferNameCell } from 'components/OffersTable/Cells/OfferNameCell/OfferNameCell'
import { OfferVenueCell } from 'components/OffersTable/Cells/OfferVenueCell'
import { ThumbCell } from 'components/OffersTable/Cells/ThumbCell'

import { AddressCell } from './components/AddressCell'
import { IndividualActionsCells } from './components/IndividualActionsCell'
import { OfferRemainingStockCell } from './components/OfferRemainingStockCell'
import { OfferStatusCell } from './components/OfferStatusCell'
import styles from './IndividualOfferRow.module.scss'

export type IndividualOfferRowProps = {
  isSelected: boolean
  offer: ListOffersOfferResponseModel
  selectOffer: (offer: ListOffersOfferResponseModel) => void
  isFirstRow: boolean
  isRestrictedAsAdmin: boolean
}

export const IndividualOfferRow = ({
  offer,
  isSelected,
  selectOffer,
  isFirstRow,
  isRestrictedAsAdmin,
}: IndividualOfferRowProps) => {
  const offerAddressEnabled = useActiveFeature('WIP_ENABLE_OFFER_ADDRESS')

  const editionOfferLink = useOfferEditionURL({
    isOfferEducational: false,
    offerId: offer.id,
    isShowcase: false,
    status: offer.status,
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
        [styles['is-first-row']]: isFirstRow,
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

      {offerAddressEnabled ? (
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
        isRestrictedAsAdmin={isRestrictedAsAdmin}
      />
    </tr>
  )
}
