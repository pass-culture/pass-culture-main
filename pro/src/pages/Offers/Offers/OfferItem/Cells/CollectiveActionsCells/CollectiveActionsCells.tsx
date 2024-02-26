import React from 'react'

import { OfferStatus } from 'apiClient/v1'
import { Offer } from 'core/Offers/types'

import styles from '../../OfferItem.module.scss'
import { BookingLinkCell } from '../BookingLinkCell/BookingLinkCell'
import DuplicateOfferCell from '../DuplicateOfferCell/DuplicateOfferCell'
import EditOfferCell from '../EditOfferCell'

interface ActionsCellsProps {
  offer: Offer
  isOfferEditable: boolean
  editionOfferLink: string
}

const CollectiveActionsCells = ({
  offer,
  isOfferEditable,
  editionOfferLink,
}: ActionsCellsProps) => {
  return (
    <td className={styles['actions-column']}>
      <div className={styles['actions-column-container']}>
        <DuplicateOfferCell offerId={offer.id} isShowcase={offer.isShowcase} />
        {(offer.status == OfferStatus.SOLD_OUT ||
          offer.status == OfferStatus.EXPIRED) &&
          offer.educationalBooking && (
            <BookingLinkCell
              bookingId={offer.educationalBooking?.id}
              bookingStatus={offer.educationalBooking.booking_status}
              offerEventDate={offer.stocks[0].beginningDatetime}
            />
          )}
        {offer.isEditable && !offer.isPublicApi && (
          <EditOfferCell
            offer={offer}
            isOfferEditable={isOfferEditable}
            editionOfferLink={editionOfferLink}
          />
        )}
      </div>
    </td>
  )
}

export default CollectiveActionsCells
