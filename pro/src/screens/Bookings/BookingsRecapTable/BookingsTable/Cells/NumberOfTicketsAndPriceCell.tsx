import { CollectiveBookingResponseModel } from 'apiClient/v1'
import { formatPrice } from 'utils/formatPrice'
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
      <div>
        {formatPrice(booking.bookingAmount, {
          minimumFractionDigits: 2,
          maximumFractionDigits: 2,
          trailingZeroDisplay: 'stripIfInteger',
        })}
      </div>
    </div>
  )
}
