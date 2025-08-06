import cn from 'classnames'
import { useState } from 'react'

import { BookingRecapResponseModel } from '@/apiClient//v1'
import { formatPrice } from '@/commons/utils/formatPrice'
import strokeDuoIcon from '@/icons/stroke-duo.svg'
import { SvgIcon } from '@/ui-kit/SvgIcon/SvgIcon'

import styles from './BookingsTable.module.scss'
import { BeneficiaryCell } from './Cells/BeneficiaryCell'
import { BookingDateCell } from './Cells/BookingDateCell'
import { BookingOfferCell } from './Cells/BookingOfferCell'
import { BookingStatusCellHistory } from './Cells/BookingStatusCellHistory'
import { DetailsButtonCell } from './Cells/DetailsButtonCell'
import { IndividualBookingStatusCell } from './Cells/IndividualBookingStatusCell'

export interface IndividualTableRowProps {
  booking: BookingRecapResponseModel
  index: number
}

const computeBookingAmount = (amount: number) =>
  amount ? formatPrice(amount) : 'Gratuit'

export const IndividualTableRow = ({
  booking,
  index,
}: IndividualTableRowProps) => {
  const [isExpanded, setIsExpanded] = useState(false)

  return (
    <>
      <tr className={styles['table-row']}>
        <td
          className={cn(styles['table-cell'], styles['column-offer-name'])}
          data-label="Nom de l’offre"
        >
          <div
            className={cn(
              styles['cell-item-wrapper'],
              styles['offer-details-wrapper']
            )}
          >
            <BookingOfferCell booking={booking} />

            {booking.bookingIsDuo && (
              <SvgIcon
                src={strokeDuoIcon}
                alt="Réservation DUO"
                className={styles['bookings-duo-icon']}
              />
            )}
          </div>
        </td>

        <td
          className={cn(styles['table-cell'], styles['column-beneficiary'])}
          data-label="Bénéficiaire"
        >
          <BeneficiaryCell
            beneficiaryInfos={booking.beneficiary}
            className={styles['cell-item-wrapper']}
          />
        </td>

        <td
          className={cn(styles['table-cell'], styles['column-booking-date'])}
          data-label="Réservation"
        >
          <BookingDateCell
            bookingDateTimeIsoString={booking.bookingDate}
            className={styles['cell-item-wrapper']}
          />
        </td>

        <td
          className={cn(styles['table-cell'], styles['column-booking-token'])}
          data-label="Contremarque"
        >
          <span className={styles['cell-item-wrapper']}>
            {booking.bookingToken || '-'}
          </span>
        </td>

        <td
          className={cn(styles['table-cell'], styles['column-booking-status'])}
          data-label="Statut"
        >
          <IndividualBookingStatusCell
            booking={booking}
            className={styles['cell-item-wrapper']}
          />
        </td>

        <td className={cn(styles['table-cell'])} data-label="Détails">
          <DetailsButtonCell
            controlledId={`booking-details-${index}`}
            isExpanded={isExpanded}
            className={styles['cell-item-wrapper']}
            onClick={() => {
              setIsExpanded((prev) => !prev)
            }}
          />
        </td>
      </tr>
      {isExpanded && (
        <tr id={`booking-details-${index}`} className={styles['details-row']}>
          <td className={styles['details-cell']} colSpan={6}>
            <div>
              <span className={styles['details-title']}>Prix : </span>
              <span
                className={styles['details-content']}
              >{`${computeBookingAmount(booking.bookingAmount)}`}</span>
            </div>
            <BookingStatusCellHistory
              index={index}
              bookingStatusHistory={booking.bookingStatusHistory}
            />
          </td>
        </tr>
      )}
    </>
  )
}
