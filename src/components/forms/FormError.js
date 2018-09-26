/* eslint
  react/jsx-one-expression-per-line: 0 */
import React from 'react'
import PropTypes from 'prop-types'

// NOTE: les index d'array ne doit pas servir de clé unique
// pour les éléments d'une liste d'éléménts
// ici on considére que l'élément à afficher n'est pas sensible aux updates
// car il s'agit de simple message d'erreur de formulaire
// Documentation: https://reactjs.org/docs/lists-and-keys.html#keys
const setDangerousArrayKeyIndex = index => `field_error_${index}`

/* azertyazertyP0 */
export const FormError = ({ className, customMessage, meta }) => {
  // TODO -> faudra scinder le composant en deux
  // un composant pour les erreurs de form
  // un composant pour les erreurs de fields
  const showError =
    customMessage ||
    (meta &&
      meta.touched &&
      (meta.error || (!meta.dirtySinceLastSubmit && meta.submitError)))
  let errorMessage =
    (showError &&
      (customMessage ||
        (meta.error || (!meta.dirtySinceLastSubmit && meta.submitError)))) ||
    null
  // FIXME -> transformation en array plus propre
  // on considére qu'une erreur est soit un string, soit un array
  errorMessage = !errorMessage
    ? null
    : (Array.isArray(errorMessage) && errorMessage) || [].concat(errorMessage)
  return (
    <span className={`pc-final-form-errors is-block mt7 ${className}`}>
      {(errorMessage && (
        <span className="flex-columns is-primary-text">
          <span className="flex-0 mr3">
            <span aria-hidden className="icon-warning-circled fs18" title="" />
          </span>
          <span className="flex-1 is-semi-bold fs15">
            {errorMessage.map((err, index) => (
              <span
                key={setDangerousArrayKeyIndex(index)}
                className="pc-error-message is-block mt2"
              >
                {err}
              </span>
            ))}
          </span>
        </span>
      )) ||
        null}
    </span>
  )
}

FormError.defaultProps = {
  className: '',
  customMessage: '',
  meta: null,
}

FormError.propTypes = {
  className: PropTypes.string,
  // NOTE: utile uniquement pour afficher un message custom
  // ne doit pas faire doublon avec les erreurs générées par le form
  // doit être utilisé par exemple pour passer une erreur générale de formulaire
  customMessage: PropTypes.string,
  // NOTE: les erreurs des fields sont générées automatiquement
  // par le formulaire via la propriété `meta`
  // Exemple: https://codesandbox.io/s/9y9om95lyp
  // Documentation: https://github.com/final-form/react-final-form
  meta: PropTypes.object,
}

export default FormError
