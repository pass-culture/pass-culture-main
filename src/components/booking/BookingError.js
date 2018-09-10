/* eslint
  react/jsx-one-expression-per-line: 0 */
import React from 'react'
import PropTypes from 'prop-types'
import { Icon } from 'pass-culture-shared'

// NOTE: hack pour contourner le no-array-index-key
// !!! BAD PRACTICE mais permise ici car ce n'est pas un affiche critique
// lire plus -> https://reactjs.org/docs/lists-and-keys.html#keys
const getArrayIndex = index => `error_${index}`

const flattenErrors = (acc, err) => {
  let value = err
  if (Array.isArray(err)) value = Array.prototype.concat.apply([], err)
  return acc.concat(value)
}

const BookingError = ({ errors }) => {
  // NOTE: 404, 500 -> donne un array
  // sinon donne un object, on veut afficher les erreurs aux users
  // donc on garde que le cas de l'object
  const entries =
    errors && !Array.isArray(errors) && typeof errors === 'object'
      ? Object.values(errors).reduce(flattenErrors, [])
      : []
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
        <p className="mb36">Une erreur est survenue lors de la réservation</p>
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
