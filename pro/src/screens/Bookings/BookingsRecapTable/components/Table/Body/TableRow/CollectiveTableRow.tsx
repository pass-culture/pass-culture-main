import React, { useContext, useEffect, useRef, useState } from 'react'
import type { Row } from 'react-table'

import { CollectiveBookingResponseModel } from 'apiClient/v1'
import { CollectiveBookingByIdResponseModel } from 'apiClient/v1/models/CollectiveBookingByIdResponseModel'
import { Events } from 'core/FirebaseEvents/constants'
import useActiveFeature from 'hooks/useActiveFeature'
import useAnalytics from 'hooks/useAnalytics'
import { RowExpandedContext } from 'screens/Bookings/BookingsRecapTable/BookingsRecapTable'
import Spinner from 'ui-kit/Spinner/Spinner'
import { doesUserPreferReducedMotion } from 'utils/windowMatchMedia'

import CollectiveBookingDetails from '../CollectiveBookingDetails'
import OldCollectiveBookingDetails from '../OldCollectiveBookingDetails'

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
  const isImproveCollectiveStatusActive = useActiveFeature(
    'WIP_IMPROVE_COLLECTIVE_STATUS'
  )

  const detailsRef = useRef<HTMLTableRowElement | null>(null)
  const rowToExpandContext = useContext(RowExpandedContext)

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

  useEffect(() => {
    // We expand row if bookingId match the one in the context
    if (rowToExpandContext.rowToExpandId == row.original.booking_id) {
      row.toggleRowExpanded(true)
    }
  }, [row, rowToExpandContext])

  useEffect(() => {
    if (detailsRef.current && !isLoading && rowToExpandContext.shouldScroll) {
      detailsRef.current?.scrollIntoView({
        behavior: doesUserPreferReducedMotion() ? 'auto' : 'smooth',
      })
      rowToExpandContext.setShouldScroll(false)
    }
  }, [rowToExpandContext.shouldScroll, detailsRef.current, isLoading])

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
          <tr className={styles['details-container']} ref={detailsRef}>
            {isLoading ? (
              <td className={styles['loader']}>
                <Spinner />
              </td>
            ) : (
              bookingDetails && (
                <td className={styles['details-content']}>
                  {isImproveCollectiveStatusActive ? (
                    <CollectiveBookingDetails
                      bookingDetails={bookingDetails}
                      bookingRecap={row.original}
                      reloadBookings={reloadBookings}
                    />
                  ) : (
                    <OldCollectiveBookingDetails
                      bookingDetails={bookingDetails}
                      offerId={row.original.stock.offer_identifier}
                      canCancelBooking={bookingDetails.isCancellable}
                      reloadBookings={reloadBookings}
                    />
                  )}
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
