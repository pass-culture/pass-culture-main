/* eslint
  react/jsx-one-expression-per-line: 0 */
import React from 'react'

const BookingCardLoader = () => (
  <div
    style={{ height: '100%' }}
    className="loading flex-rows flex-1 items-center flex-center loading"
  >
    <span>Réservation en cours...</span>
  </div>
)

export default BookingCardLoader
