import React from 'react'
import get from 'lodash.get'
import PropTypes from 'prop-types'

const BookingHeader = ({ recommendation }) => {
  const { offer } = recommendation || {}
  const title = get(offer, 'name')
  const subtitle = get(offer, 'venue.name')
  return (
    <header className="flex-0">
      <h1 className="title">
        <span>{title}</span>
      </h1>
      <h2 className="subtitle">
        <span>{subtitle}</span>
      </h2>
    </header>
  )
}

BookingHeader.defaultProps = {
  recommendation: null,
}

BookingHeader.propTypes = {
  recommendation: PropTypes.shape(),
}

export default BookingHeader
