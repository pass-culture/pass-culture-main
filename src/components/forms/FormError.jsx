import React from 'react'
import PropTypes from 'prop-types'

import Icon from '../layout/Icon/Icon'

// NOTE: les index d'array ne doit pas servir de clé unique
// pour les éléments d'une liste d'éléménts
// ici on considére que l'élément à afficher n'est pas sensible aux updates
// car il s'agit de simple message d'erreur de formulaire
// Documentation: https://reactjs.org/docs/lists-and-keys.html#keys
const setDangerousArrayKeyIndex = index => `field_error_${index}`

const FormError = ({ customMessage, meta }) => {
  const showError =
    customMessage ||
    (meta && meta.touched && (meta.error || (!meta.dirtySinceLastSubmit && meta.submitError)))
  let errorMessages =
    (showError &&
      (customMessage || (meta.error || (!meta.dirtySinceLastSubmit && meta.submitError)))) ||
    null
  // FIXME -> transformation en array plus propre
  // on considére qu'une erreur est soit un string, soit un array
  errorMessages = !errorMessages
    ? null
    : (Array.isArray(errorMessages) && errorMessages) || [].concat(errorMessages)

  return (
    (errorMessages && (
      <div className="mt7">
        <div className="flex-columns">
          <div className="flex-0">
            <Icon
              className="picto-error"
              svg="picto-info-b"
            />
          </div>
          <div className="flex-1">
            {errorMessages.map((error, index) => (
              <div
                className="form-error-message"
                key={setDangerousArrayKeyIndex(index)}
              >
                {error}
              </div>
            ))}
          </div>
        </div>
      </div>
    )) ||
    null
  )
}

FormError.defaultProps = {
  customMessage: '',
  meta: null,
  theme: 'white',
}

FormError.propTypes = {
  // NOTE: utile uniquement pour afficher un message custom
  // ne doit pas faire doublon avec les erreurs générées par le form
  // doit être utilisé par exemple pour passer une erreur générale de formulaire
  customMessage: PropTypes.string,
  // NOTE: les erreurs des fields sont générées automatiquement
  // par le formulaire via la propriété `meta`
  // Exemple: https://codesandbox.io/s/9y9om95lyp
  // Documentation: https://github.com/final-form/react-final-form
  meta: PropTypes.shape(),
  theme: PropTypes.string,
}

export default FormError
