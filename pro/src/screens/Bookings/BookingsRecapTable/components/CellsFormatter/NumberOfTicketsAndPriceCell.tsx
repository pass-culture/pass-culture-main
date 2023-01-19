import React from 'react'
import { Row } from 'react-table'

import { CollectiveBookingResponseModel } from 'apiClient/v1'
import { pluralizeString } from 'utils/pluralize'

const NumberOfTicketsAndPriceCell = ({
  bookingRecapInfo,
}: {
  bookingRecapInfo: Row<CollectiveBookingResponseModel>
}) => {
  const numberOfTickets = bookingRecapInfo.original.stock.numberOfTickets
  return (
    <div>
      <div>
        {numberOfTickets} {pluralizeString('place', numberOfTickets)}
      </div>
      <div>{bookingRecapInfo.original.bookingAmount}€</div>
    </div>
  )
}

export default NumberOfTicketsAndPriceCell
