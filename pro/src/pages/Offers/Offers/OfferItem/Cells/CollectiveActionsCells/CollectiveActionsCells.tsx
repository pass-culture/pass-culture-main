import React from 'react'

import { CollectiveOfferResponseModel, OfferStatus } from 'apiClient/v1'

import styles from '../../OfferItem.module.scss'
import { BookingLinkCell } from '../BookingLinkCell/BookingLinkCell'
import DuplicateOfferCell from '../DuplicateOfferCell/DuplicateOfferCell'
import { EditOfferCell } from '../EditOfferCell/EditOfferCell'

interface CollectiveActionsCellsProps {
  offer: CollectiveOfferResponseModel
  editionOfferLink: string
}

export const CollectiveActionsCells = ({
  offer,
  editionOfferLink,
}: CollectiveActionsCellsProps) => {
  return (
    <td className={styles['actions-column']}>
      <div className={styles['actions-column-container']}>
        <DuplicateOfferCell offerId={offer.id} isShowcase={offer.isShowcase} />

        {(offer.status == OfferStatus.SOLD_OUT ||
          offer.status == OfferStatus.EXPIRED) &&
          offer.booking && (
            <BookingLinkCell
              bookingId={offer.booking.id}
              bookingStatus={offer.booking.booking_status}
              offerEventDate={offer.stocks[0].beginningDatetime}
            />
          )}

        {offer.isEditable && !offer.isPublicApi && (
          <EditOfferCell editionOfferLink={editionOfferLink} />
        )}
      </div>
    </td>
  )
}
