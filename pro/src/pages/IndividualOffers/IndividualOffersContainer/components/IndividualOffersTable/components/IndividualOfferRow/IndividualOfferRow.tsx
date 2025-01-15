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

import { AddressCell } from './components/AddressCell'
import { IndividualActionsCells } from './components/IndividualActionsCells'
import { OfferRemainingStockCell } from './components/OfferRemainingStockCell'
import { OfferStatusCell } from './components/OfferStatusCell'
import styles from './IndividualOfferRow.module.scss'

export type IndividualOfferRowProps = {
  isSelected: boolean
  offer: ListOffersOfferResponseModel
  selectOffer: (offer: ListOffersOfferResponseModel) => void
  isRestrictedAsAdmin: boolean
}

export const IndividualOfferRow = ({
  offer,
  isSelected,
  selectOffer,
  isRestrictedAsAdmin,
}: IndividualOfferRowProps) => {
  const rowId = `collective-offer-${offer.id}`
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

  return (
    <tr
      role="row"
      className={styles['individual-row']}
      data-testid="offer-item-row"
    >
      <CheckboxCell
        rowId={rowId}
        offerName={offer.name}
        isSelected={isSelected}
        disabled={isOfferDisabled(offer.status)}
        selectOffer={() => selectOffer(offer)}
        className={styles['individual-cell-checkbox']}
      />
      <OfferNameCell
        rowId={rowId}
        offer={offer}
        offerLink={offerLink}
        className={styles['individual-cell-name']}
        displayLabel
        displayThumb
      />
      {offerAddressEnabled ? (
        <AddressCell
          rowId={rowId}
          address={offer.address}
          className={styles['individual-cell-venue']}
          displayLabel
        />
      ) : (
        <OfferVenueCell
          rowId={rowId}
          venue={offer.venue}
          className={styles['individual-cell-venue']}
          displayLabel
        />
      )}
      <OfferRemainingStockCell
        rowId={rowId}
        stocks={offer.stocks}
        className={styles['individual-cell-stock']}
        displayLabel
      />
      <OfferStatusCell
        rowId={rowId}
        status={offer.status}
        className={styles['individual-cell-status']}
        displayLabel
      />
      <IndividualActionsCells
        rowId={rowId}
        offer={offer}
        editionOfferLink={offerLink}
        editionStockLink={editionStockLink}
        isRestrictedAsAdmin={isRestrictedAsAdmin}
        className={styles['individual-cell-actions']}
      />
    </tr>
  )
}
