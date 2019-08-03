import PropTypes from 'prop-types'
import React from 'react'

const BookingHeader = ({ offer }) => {
  const { name: title, venue } = offer || {}
  const { name: subtitle } = venue || {}
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
  offer: null,
}

BookingHeader.propTypes = {
  offer: PropTypes.shape({
    name: PropTypes.string,
    venue: PropTypes.shape({
      name: PropTypes.string
    })
  }),
}

export default BookingHeader
