import React from 'react'

import { OFFER_STATUS_DRAFT } from 'core/Offers'
import { Offer } from 'core/Offers/types'

import styles from '../../OfferItem.module.scss'
import DeleteDraftCell from '../DeleteDraftCell'
import EditOfferCell from '../EditOfferCell'
import EditStocksCell from '../EditStocksCell'

interface IActionsCellsProps {
  offer: Offer
  isOfferEditable: boolean
  editionOfferLink: string
  editionStockLink: string
  refreshOffers: () => void
}

const IndividualActionsCells = ({
  offer,
  isOfferEditable,
  editionOfferLink,
  editionStockLink,
  refreshOffers,
}: IActionsCellsProps) => {
  return (
    <td className={styles['actions-column']}>
      <div className={styles['actions-column-container']}>
        {offer.status === OFFER_STATUS_DRAFT ? (
          <DeleteDraftCell offer={offer} refreshOffers={refreshOffers} />
        ) : (
          <EditStocksCell offer={offer} editionStockLink={editionStockLink} />
        )}

        <EditOfferCell
          isOfferEditable={isOfferEditable}
          editionOfferLink={editionOfferLink}
          offer={offer}
        />
      </div>
    </td>
  )
}

export default IndividualActionsCells
