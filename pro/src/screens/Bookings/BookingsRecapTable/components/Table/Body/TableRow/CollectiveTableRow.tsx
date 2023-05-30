import React, { useEffect, useRef, useState } from 'react'
import type { Row } from 'react-table'

import { CollectiveBookingResponseModel } from 'apiClient/v1'
import { CollectiveBookingByIdResponseModel } from 'apiClient/v1/models/CollectiveBookingByIdResponseModel'
import { CollectiveBookingsEvents } from 'core/FirebaseEvents/constants'
import useAnalytics from 'hooks/useAnalytics'
import Spinner from 'ui-kit/Spinner/Spinner'
import { doesUserPreferReducedMotion } from 'utils/windowMatchMedia'

import CollectiveBookingDetails from '../CollectiveBookingDetails'

import getCollectiveBookingAdapter from './adapters/getCollectiveBookingAdapter'
import TableRow from './TableRow'
import styles from './TableRow.module.scss'

export interface ITableBodyProps {
  row: Row<CollectiveBookingResponseModel>
  reloadBookings: () => void
  bookingId: string
}

const CollectiveTableRow = ({
  row,
  reloadBookings,
  bookingId,
}: ITableBodyProps) => {
  const [bookingDetails, setBookingDetails] =
    useState<CollectiveBookingByIdResponseModel | null>(null)
  const [isLoading, setIsLoading] = useState(false)
  const { logEvent } = useAnalytics()

  const detailsRef = useRef<HTMLTableRowElement | null>(null)

  useEffect(() => {
    const fetchBookingDetails = async () => {
      setIsLoading(true)
      const bookingResponse = await getCollectiveBookingAdapter(
        row.original.bookingIdentifier
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

  /* istanbul ignore next: DEBT, TO FIX need to mock useTable entirely */
  const onRowClick = () => {
    logEvent?.(
      CollectiveBookingsEvents.CLICKED_EXPAND_COLLECTIVE_BOOKING_DETAILS
    )
    row.toggleRowExpanded()
  }

  useEffect(() => {
    // We expand row if bookingId match the one in the context

    if (bookingId == row.original.bookingId) {
      row.toggleRowExpanded(true)
      setTimeout(
        () =>
          detailsRef?.current?.scrollIntoView({
            behavior: doesUserPreferReducedMotion() ? 'auto' : 'smooth',
          }),
        100
      )
    }
  }, [row, bookingId])

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
          <tr className={styles['details-container']} ref={detailsRef}>
            {isLoading ? (
              <td className={styles['loader']}>
                <Spinner />
              </td>
            ) : (
              bookingDetails && (
                <td className={styles['details-content']} id={bookingId}>
                  <CollectiveBookingDetails
                    bookingDetails={bookingDetails}
                    bookingRecap={row.original}
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
