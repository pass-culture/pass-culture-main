import React from 'react'

import { OFFER_STATUS_DRAFT } from 'core/Offers/constants'
import { Offer } from 'core/Offers/types'

import styles from '../../OfferItem.module.scss'
import DeleteDraftCell from '../DeleteDraftCell'
import { EditOfferCell } from '../EditOfferCell/EditOfferCell'
import EditStocksCell from '../EditStocksCell'

interface IndividualActionsCellsProps {
  offer: Offer
  editionOfferLink: string
  editionStockLink: string
  refreshOffers: () => void
}

export const IndividualActionsCells = ({
  offer,
  editionOfferLink,
  editionStockLink,
  refreshOffers,
}: IndividualActionsCellsProps) => {
  return (
    <td className={styles['actions-column']}>
      <div className={styles['actions-column-container']}>
        {offer.status === OFFER_STATUS_DRAFT ? (
          <DeleteDraftCell offer={offer} refreshOffers={refreshOffers} />
        ) : (
          <EditStocksCell offer={offer} editionStockLink={editionStockLink} />
        )}

        <EditOfferCell editionOfferLink={editionOfferLink} />
      </div>
    </td>
  )
}
