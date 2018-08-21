/* eslint
  react/jsx-one-expression-per-line: 0 */
import React from 'react'
import PropTypes from 'prop-types'

const BookingCardError = ({ errors, config }) => (
  <div>
    <h1 className="mb12">Errors</h1>
    <ul>
      {errors &&
        Object.keys(errors).map(k => (
          <li key={k} className="mb12">
            <b className="is-block">{`${k}: `}</b>
            <i className="is-block">{errors[k].toString()}</i>
          </li>
        ))}
    </ul>
    <h1 className="mt20 mb12">Config</h1>
    <ul>
      {config &&
        config.body &&
        Object.keys(config.body).map(k => (
          <li key={k} className="mb12">
            <b className="is-block">{`${k}: `}</b>
            <i className="is-block">{config.body[k].toString()}</i>
          </li>
        ))}
    </ul>
  </div>
)

BookingCardError.propTypes = {
  config: PropTypes.object.isRequired,
  errors: PropTypes.object.isRequired,
}

export default BookingCardError
