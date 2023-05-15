import React from 'react'

import { OfferStatus } from 'apiClient/v1'
import { Offer } from 'core/Offers/types'

import styles from '../../OfferItem.module.scss'
import BookingLinkCell from '../BookingLinkCell'
import DuplicateOfferCell from '../DuplicateOfferCell/DuplicateOfferCell'
import EditOfferCell from '../EditOfferCell'

interface IActionsCellsProps {
  offer: Offer
  isOfferEditable: boolean
  editionOfferLink: string
}

const CollectiveActionsCells = ({
  offer,
  isOfferEditable,
  editionOfferLink,
}: IActionsCellsProps) => {
  return (
    <td className={styles['actions-column']}>
      <div className={styles['actions-column-container']}>
        {Boolean(offer.isShowcase) && (
          <DuplicateOfferCell templateOfferId={offer.nonHumanizedId} />
        )}
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
