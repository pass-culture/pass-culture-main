import React from 'react'

import { CollectiveBookingResponseModel } from 'apiClient/v1'
import { pluralizeString } from 'utils/pluralize'

interface NumberOfTicketsAndPriceCellProps {
  booking: CollectiveBookingResponseModel
}

export const NumberOfTicketsAndPriceCell = ({
  booking,
}: NumberOfTicketsAndPriceCellProps) => {
  const numberOfTickets = booking.stock.numberOfTickets

  return (
    <div>
      <div>
        {numberOfTickets} {pluralizeString('place', numberOfTickets)}
      </div>
      <div>{booking.bookingAmount}€</div>
    </div>
  )
}
