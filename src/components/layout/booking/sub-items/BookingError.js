import PropTypes from 'prop-types'
import React, { Component } from 'react'

import { flattenErrors } from '../helpers'
import Icon from '../../Icon'

class BookingError extends Component {
  // NOTE: hack pour contourner le no-array-index-key
  // lire plus -> https://reactjs.org/docs/lists-and-keys.html#keys
  getArrayIndex = index => `error_${index}`

  renderErrorReason = (msg, index) => {
    if (!msg) return null
    return (
      <p
        data-index={index}
        key={this.getArrayIndex(index)}
      >
        {msg}
      </p>
    )
  }

  render() {
    const { errors } = this.props
    const entries =
      errors && !Array.isArray(errors) && typeof errors === 'object'
        ? Object.values(errors).reduce(flattenErrors, [])
        : []
    return (
      <div className="booked text-center">
        <h3 className="mb16">
          <span className="is-block">
            <Icon
              alt="erreur"
              svg="picto-echec"
            />
          </span>
        </h3>
        <div
          className="fs20"
          id="booking-error-reasons"
        >
          <p className="mb36">{'Une erreur est survenue lors de la réservation'}</p>
          {entries && entries.map(this.renderErrorReason)}
        </div>
      </div>
    )
  }
}

BookingError.propTypes = {
  errors: PropTypes.oneOfType([PropTypes.array, PropTypes.shape()]).isRequired,
}

export default BookingError
