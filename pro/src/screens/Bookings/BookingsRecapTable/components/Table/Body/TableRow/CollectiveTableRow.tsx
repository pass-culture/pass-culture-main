import React, { useEffect, useState } from 'react'
import type { Row } from 'react-table'

import { CollectiveBookingResponseModel } from 'apiClient/v1'
import { CollectiveBookingByIdResponseModel } from 'apiClient/v1/models/CollectiveBookingByIdResponseModel'
import Spinner from 'components/layout/Spinner'

import CollectiveBookingDetails from '../CollectiveBookingDetails'

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

  return (
    <>
      <TableRow row={row} />
      {row.isExpanded && (
        <>
          <tr />
          <tr className={styles['details-container']}>
            {isLoading ? (
              <Spinner className={styles['loader']} />
            ) : (
              bookingDetails && (
                <CollectiveBookingDetails
                  bookingDetails={bookingDetails}
                  offerId={row.original.stock.offer_identifier}
                  reloadBookings={reloadBookings}
                />
              )
            )}
          </tr>
        </>
      )}
    </>
  )
}

export default CollectiveTableRow
