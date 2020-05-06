import React from 'react'

const BookingOfferCell = ({ stock }) => {
  const { offer_name } = stock
  return (<span className="cell-offer-link">
    {offer_name}
  </span>)
}

export default BookingOfferCell
