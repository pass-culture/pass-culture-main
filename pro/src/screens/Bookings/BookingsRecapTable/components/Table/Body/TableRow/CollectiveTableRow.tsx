import React, { useEffect, useState } from 'react'
import type { Row } from 'react-table'

import { CollectiveBookingResponseModel } from 'apiClient/v1'
import { CollectiveBookingByIdResponseModel } from 'apiClient/v1/models/CollectiveBookingByIdResponseModel'

import CollectiveBookingDetails from '../CollectiveBookingDetails'

import getCollectiveBookingAdapter from './adapters/getCollectiveBookingAdapter'
import TableRow from './TableRow'
import styles from './TableRow.module.scss'

interface ITableBodyProps {
  row: Row<CollectiveBookingResponseModel>
}

const CollectiveTableRow = ({ row }: ITableBodyProps) => {
  const [bookingDetails, setBookingDetails] =
    useState<CollectiveBookingByIdResponseModel | null>(null)

  useEffect(() => {
    const fetchBookingDetails = async () => {
      const bookingResponse = await getCollectiveBookingAdapter(
        row.original.booking_identifier
      )
      if (bookingResponse.isOk) {
        setBookingDetails(bookingResponse.payload)
      }
    }

    if (row.isExpanded && bookingDetails === null) {
      fetchBookingDetails()
    }
  }, [row.isExpanded])

  return (
    <>
      <TableRow row={row} />
      {row.isExpanded && bookingDetails && (
        <>
          <tr />
          <tr className={styles['details-container']}>
            <CollectiveBookingDetails bookingDetails={bookingDetails} />
          </tr>
        </>
      )}
    </>
  )
}

export default CollectiveTableRow
