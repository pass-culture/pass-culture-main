import PropTypes from 'prop-types'
import React from 'react'

import Icon from '../Icon'

// NOTE: les index d'array ne doit pas servir de clé unique
// pour les éléments d'une liste d'éléménts
// ici on considére que l'élément à afficher n'est pas sensible aux updates
// car il s'agit de simple message d'erreur de formulaire
// Documentation: https://reactjs.org/docs/lists-and-keys.html#keys
const setDangerousArrayKeyIndex = index => `field_error_${index}`

const FieldErrors = ({ className, customMessage, meta }) => {
  const showError =
    customMessage ||
    (meta &&
      meta.touched &&
      (meta.error || (!meta.dirtySinceLastSubmit && meta.submitError)))
  let errorMessage =
    (showError &&
      (customMessage ||
        meta.error ||
        (!meta.dirtySinceLastSubmit && meta.submitError))) ||
    null
  // FIXME -> transformation en array plus propre
  // on considére qu'une erreur est soit un string, soit un array
  errorMessage = !errorMessage
    ? null
    : (Array.isArray(errorMessage) && errorMessage) || [].concat(errorMessage)
  return (
    (errorMessage && (
      <span className={`field-errors ${className}`}>
        <span className="field-error-icon">
          <Icon
            alt="Une erreur est survenue"
            svg="ico-notification-error-red"
          />
        </span>
        <span className="field-error-messages">
          {errorMessage.map((err, index) => (
            <p
              className="field-error-message"
              key={setDangerousArrayKeyIndex(index)}
            >
              {err}
            </p>
          ))}
        </span>
      </span>
    )) ||
    null
  )
}

FieldErrors.defaultProps = {
  className: '',
  customMessage: '',
  meta: null,
}

FieldErrors.propTypes = {
  className: PropTypes.string,
  // NOTE: utile uniquement pour afficher un message custom
  // ne doit pas faire doublon avec les erreurs générées par le form
  // doit être utilisé par exemple pour passer une erreur générale de formulaire
  customMessage: PropTypes.string,
  // NOTE: les erreurs des fields sont générées automatiquement
  // par le formulaire via la propriété `meta`
  // Exemple: https://codesandbox.io/s/9y9om95lyp
  // Documentation: https://github.com/final-form/react-final-form
  meta: PropTypes.shape(),
}

export default FieldErrors
