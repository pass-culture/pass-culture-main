import React from 'react'
import PropTypes from 'prop-types'

const BookingItem = ({ booking }) => (
  <li className="offer-item">
    <div className="list-content">
      <ul className="infos">
        <li>ID: {booking.id}</li>
        <li>amount : {booking.amount}</li>
        {/*
        <li>dateModified : {booking.dateModified}</li>
        <li>dehumanizedId : {booking.dehumanizedId}</li>
        <li>
          dehumanizedRecommendationId : {booking.dehumanizedRecommendationId}
        </li>
        <li>dehumanizedStockId : {booking.dehumanizedStockId}</li>
        <li>dehumanizedUserId : {booking.dehumanizedUserId}</li>
        <li>isActive : {booking.isActive}</li>
        */}
        <li>modelName : {booking.modelName}</li>
        <li>quantity : {booking.quantity}</li>
        {/*
        <li>recommendationId : {booking.recommendationId}</li>
        <li>reimbursed_amount : {booking.reimbursed_amount}</li>
        <li>reimbursement_rule : {booking.reimbursement_rule}</li>
        <li>stockId : {booking.stockId}</li>
        */}
        <li>token : {booking.token}</li>
        <li>userId : {booking.userId}</li>
      </ul>
    </div>
  </li>
)

BookingItem.propTypes = {
  booking: PropTypes.object.isRequired,
}

export default BookingItem
