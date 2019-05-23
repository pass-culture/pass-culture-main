/* eslint
  react/jsx-one-expression-per-line: 0 */
import PropTypes from 'prop-types'
import React from 'react'

import { flattenErrors } from '../utils'
import Icon from '../../layout/Icon'

// NOTE: hack pour contourner le no-array-index-key
// lire plus -> https://reactjs.org/docs/lists-and-keys.html#keys
const getArrayIndex = index => `error_${index}`

const renderErrorReason = (msg, index) => {
  if (!msg) return null
  return (
    <p data-index={index} key={getArrayIndex(index)}>
      {msg}
    </p>
  )
}

const BookingError = ({ errors }) => {
  const entries =
    errors && !Array.isArray(errors) && typeof errors === 'object'
      ? Object.values(errors).reduce(flattenErrors, [])
      : []
  return (
    <div className="booked text-center">
      <h3 className="mb16">
        <span className="is-block">
          <Icon svg="picto-echec" alt="erreur" />
        </span>
      </h3>
      <div id="booking-error-reasons" className="fs20">
        <p className="mb36">Une erreur est survenue lors de la réservation</p>
        {entries && entries.map(renderErrorReason)}
      </div>
    </div>
  )
}

BookingError.propTypes = {
  errors: PropTypes.oneOfType([PropTypes.array, PropTypes.object]).isRequired,
}

export default BookingError
