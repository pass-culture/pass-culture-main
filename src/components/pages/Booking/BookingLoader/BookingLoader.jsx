import React from 'react'

const BookingLoader = () => (
  <div
    className="loading flex-rows flex-1 items-center flex-center loading"
    style={{ height: '100%' }}
  >
    <span>{'Réservation en cours...'}</span>
  </div>
)

export default BookingLoader
