import { ListOffersOfferResponseModel } from 'apiClient/v1'
import { isOfferDisabled } from 'commons/core/Offers/utils/isOfferDisabled'
import { useActiveFeature } from 'commons/hooks/useActiveFeature'
import {
  useOfferEditionURL,
  useOfferStockEditionURL,
} from 'commons/hooks/useOfferEditionURL'
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
  const offerAddressEnabled = useActiveFeature('WIP_ENABLE_OFFER_ADDRESS')

  const editionOfferLink = useOfferEditionURL({
    isOfferEducational: false,
    offerId: offer.id,
    isShowcase: false,
    status: offer.status,
  })
  const editionStockLink = useOfferStockEditionURL(false, offer.id, false)

  return (
    <tr
      role="row"
      className={styles['individual-row']}
      data-testid="offer-item-row"
    >
      <CheckboxCell
        offerName={offer.name}
        isSelected={isSelected}
        disabled={isOfferDisabled(offer.status)}
        selectOffer={() => selectOffer(offer)}
        className={styles['individual-cell-checkbox']}
      />
      <OfferNameCell
        offer={offer}
        editionOfferLink={editionOfferLink}
        displayThumb={true}
        className={styles['individual-cell-name']}
      />
      {offerAddressEnabled ? (
        <AddressCell
          address={offer.address}
          className={styles['individual-cell-venue']}
          displayLabel
        />
      ) : (
        <OfferVenueCell
          venue={offer.venue}
          className={styles['individual-cell-venue']}
          displayLabel
        />
      )}
      <OfferRemainingStockCell
        stocks={offer.stocks}
        className={styles['individual-cell-stock']}
        displayLabel
      />
      <OfferStatusCell
        status={offer.status}
        className={styles['individual-cell-status']}
        displayLabel
      />
      <IndividualActionsCells
        offer={offer}
        editionOfferLink={editionOfferLink}
        editionStockLink={editionStockLink}
        isRestrictedAsAdmin={isRestrictedAsAdmin}
        className={styles['individual-cell-actions']}
      />
    </tr>
  )
}
