import React, { useEffect, useState } from 'react'
import type { Row } from 'react-table'

import { CollectiveBookingResponseModel } from 'apiClient/v1'
import { CollectiveBookingByIdResponseModel } from 'apiClient/v1/models/CollectiveBookingByIdResponseModel'
import { Events } from 'core/FirebaseEvents/constants'
import useAnalytics from 'hooks/useAnalytics'
import Spinner from 'ui-kit/Spinner/Spinner'

import CollectiveBookingDetails from '../OldCollectiveBookingDetails'

import getCollectiveBookingAdapter from './adapters/getCollectiveBookingAdapter'
import TableRow from './TableRow'
import styles from './TableRow.module.scss'

export interface ITableBodyProps {
  row: Row<CollectiveBookingResponseModel>
  reloadBookings: () => void
}

const CollectiveTableRow = ({ row, reloadBookings }: ITableBodyProps) => {
  const [bookingDetails, setBookingDetails] =
    useState<CollectiveBookingByIdResponseModel | null>(null)
  const [isLoading, setIsLoading] = useState(false)
  const { logEvent } = useAnalytics()

  useEffect(() => {
    const fetchBookingDetails = async () => {
      setIsLoading(true)
      const bookingResponse = await getCollectiveBookingAdapter(
        row.original.booking_identifier
      )
      if (bookingResponse.isOk) {
        setBookingDetails(bookingResponse.payload)
      }
      setIsLoading(false)
    }

    if (row.isExpanded && bookingDetails === null) {
      fetchBookingDetails()
    }
  }, [row.isExpanded])

  const onRowClick = () => {
    logEvent?.(Events.CLICKED_EXPAND_COLLECTIVE_BOOKING_DETAILS)
    row.toggleRowExpanded()
  }

  return (
    <>
      <TableRow
        row={row}
        additionalRowAttribute={{
          onClick: onRowClick,
          style: { cursor: 'pointer' },
        }}
      />
      {row.isExpanded && (
        <>
          <tr />
          <tr className={styles['details-container']}>
            {isLoading ? (
              <td className={styles['loader']}>
                <Spinner />
              </td>
            ) : (
              bookingDetails && (
                <td className={styles['details-content']}>
                  <CollectiveBookingDetails
                    bookingDetails={bookingDetails}
                    offerId={row.original.stock.offer_identifier}
                    canCancelBooking={bookingDetails.isCancellable}
                    reloadBookings={reloadBookings}
                  />
                </td>
              )
            )}
          </tr>
        </>
      )}
    </>
  )
}

export default CollectiveTableRow
