import React, { useEffect, useRef, useState } from 'react'
import { useLocation } from 'react-router'
import type { Row } from 'react-table'

import { CollectiveBookingResponseModel } from 'apiClient/v1'
import { CollectiveBookingByIdResponseModel } from 'apiClient/v1/models/CollectiveBookingByIdResponseModel'
import { Events } from 'core/FirebaseEvents/constants'
import useActiveFeature from 'hooks/useActiveFeature'
import useAnalytics from 'hooks/useAnalytics'
import Spinner from 'ui-kit/Spinner/Spinner'
import { doesUserPreferReducedMotion } from 'utils/windowMatchMedia'

import { EMPTY_FILTER_VALUE } from '../../../Filters'
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
  const location = useLocation()
  const queryParams = new URLSearchParams(location.search)
  const defaultBookingId = queryParams.get('bookingId') || EMPTY_FILTER_VALUE

  const detailsRef = useRef<HTMLTableRowElement | null>(null)

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
    // We expand row if bookingId match the one in query params and if there is only one row
    if (defaultBookingId === row.original.booking_id && row.index == 0) {
      row.toggleRowExpanded(true)
      if (detailsRef.current && !isLoading) {
        detailsRef.current?.scrollIntoView({
          behavior: doesUserPreferReducedMotion() ? 'auto' : 'smooth',
        })
      }
    }
  }, [row, defaultBookingId, detailsRef.current, isLoading])

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
