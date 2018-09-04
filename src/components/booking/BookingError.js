/* eslint
  react/jsx-one-expression-per-line: 0 */
import React from 'react'
import PropTypes from 'prop-types'
import { Icon } from 'pass-culture-shared'

// NOTE: hack pour contourner le no-array-index-key
// !!! BAD PRACTICE mais permise ici car ce n'est pas un affiche critique
// lire plus -> https://reactjs.org/docs/lists-and-keys.html#keys
const getArrayIndex = index => `error_${index}`

const parseErrors = (acc, errors) => {
  if (!errors) return acc
  const isstring = errors && typeof errors === 'string'
  const isobject = errors && typeof errors === 'object'
  if (isstring) return acc.concat([errors])
  if (isobject && !Array.isArray(errors)) {
    const values = Object.values(errors)
    return acc.concat(values)
  }
  return acc.concat(errors)
}

const BookingError = ({ errors }) => {
  let entries = (Array.isArray(errors) && errors) || []
  entries = entries.reduce(parseErrors, [])
  return (
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
        {entries.map(
          (msg, index) => entries && <p key={getArrayIndex(index)}>{msg}</p>
        )}
      </div>
    </div>
  )
}

BookingError.propTypes = {
  errors: PropTypes.oneOfType([PropTypes.array, PropTypes.object]).isRequired,
}

export default BookingError
