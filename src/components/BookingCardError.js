/* eslint
  react/jsx-one-expression-per-line: 0 */
import React from 'react'
import PropTypes from 'prop-types'
import { Icon } from 'pass-culture-shared'

const BookingCardError = ({ errors }) => (
  <div className="booked has-text-centered">
    <h3 style={{ fontSize: '22px' }} className="mb16">
      <span
        className="is-block"
        style={{ color: '#E60039', fontSize: '4.5rem' }}
      >
        <Icon svg="picto-echec" alt="erreur" />
      </span>
    </h3>
    <div style={{ fontSize: '20px' }}>
      <p className="mb36">Une erreur est survenue lors de la réservation :</p>
      {(typeof errors === 'object' &&
        !Array.isArray(errors) &&
        Object.keys(errors).map(key => (
          <p key={key}>{errors[key].toString()}</p>
        ))) ||
        null}
      {(typeof errors === 'object' &&
        Array.isArray(errors) &&
        errors.map((val, idx) => (
          // eslint-disable-next-line react/no-array-index-key
          <p key={`array_errors_${idx}`}>{errors[val].toString()}</p>
        ))) ||
        null}
    </div>
  </div>
)

BookingCardError.propTypes = {
  // config: PropTypes.object.isRequired,
  errors: PropTypes.oneOfType([PropTypes.array, PropTypes.object]).isRequired,
}

export default BookingCardError
