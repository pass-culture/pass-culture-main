import classNames from 'classnames'

import { ListOffersOfferResponseModel } from 'apiClient/v1'
import {
  OFFER_STATUS_DRAFT,
  OFFER_WIZARD_MODE,
} from 'commons/core/Offers/constants'
import { getIndividualOfferUrl } from 'commons/core/Offers/utils/getIndividualOfferUrl'
import { isOfferDisabled } from 'commons/core/Offers/utils/isOfferDisabled'
import { useActiveFeature } from 'commons/hooks/useActiveFeature'
import { OFFER_WIZARD_STEP_IDS } from 'components/IndividualOfferNavigation/constants'
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

  const offerLink = getIndividualOfferUrl({
    offerId: offer.id,
    mode:
      offer.status === OFFER_STATUS_DRAFT
        ? OFFER_WIZARD_MODE.CREATION
        : OFFER_WIZARD_MODE.READ_ONLY,
    step: OFFER_WIZARD_STEP_IDS.DETAILS,
  })

  const editionStockLink = getIndividualOfferUrl({
    offerId: offer.id,
    mode: OFFER_WIZARD_MODE.EDITION,
    step: OFFER_WIZARD_STEP_IDS.STOCKS,
  })

  const isOfferInactiveOrExpiredOrDisabled =
    offer.status === OFFER_STATUS_DRAFT
      ? false
      : !offer.isActive ||
        offer.hasBookingLimitDatetimesPassed ||
        isOfferDisabled(offer.status)

  return (
    <tr
      role="row"
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
      <ThumbCell offer={offer} offerLink={offerLink} />
      <OfferNameCell offer={offer} offerLink={offerLink} />
      {offerAddressEnabled ? (
        <AddressCell address={offer.address} />
      ) : (
        <OfferVenueCell venue={offer.venue} />
      )}
      <OfferRemainingStockCell stocks={offer.stocks} />
      <OfferStatusCell status={offer.status} />
      <IndividualActionsCells
        offer={offer}
        editionOfferLink={offerLink}
        editionStockLink={editionStockLink}
        isRestrictedAsAdmin={isRestrictedAsAdmin}
      />
    </tr>
  )
}
