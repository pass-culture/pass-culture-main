import React from 'react'
import PropTypes from 'prop-types'

const BookingItem = ({ booking }) => (
  <tr className="offer-item">
    <td>{booking.token}</td>
    <td>{booking.quantity}</td>
    <td
      title={`${booking.reimbursed_amount}€ remoursés sur un montant total de ${
        booking.amount
      }€`}>
      {booking.reimbursed_amount}
      &euro; / {booking.amount}
      &euro;
    </td>
    <td>{booking.reimbursement_rule}</td>
    <td>{booking.isCanceled ? 'oui' : 'non'}</td>
    {/*
    <td>ID: {booking.id}</td>
    <td>dateModified : {booking.dateModified}</td>
    <td>dehumanizedId : {booking.dehumanizedId}</td>
    <td>
      dehumanizedRecommendationId : {booking.dehumanizedRecommendationId}
    </td>
    <td>dehumanizedStockId : {booking.dehumanizedStockId}</td>
    <td>dehumanizedUserId : {booking.dehumanizedUserId}</td>
    <td>modelName : {booking.modelName}</td>
    <td>recommendationId : {booking.recommendationId}</td>
    <td>stockId : {booking.stockId}</td>
    <td>userId : {booking.userId}</td>
    */}
    <td>
      <button
        type="button"
        onClick={() => {
          if (window.confirm('Annuler cette réservation ?')) {
            console.log('ok')
          } else {
            console.log('ko')
          }
        }}>
        Annuler
      </button>
    </td>
  </tr>
)

BookingItem.propTypes = {
  booking: PropTypes.object.isRequired,
}

export default BookingItem
