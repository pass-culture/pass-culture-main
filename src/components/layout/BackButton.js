import PropTypes from 'prop-types'
import { Icon } from 'pass-culture-shared'
import React from 'react'
import { withRouter } from 'react-router'
import { compose } from 'redux'

const BackButton = ({
  history,
  match,
  location,
  className,
  // FIXME -> staticContext est défini en tant que props de composant
  // uniquement pour éviter que react-router ne lève une erreur
  // @see https://github.com/ReactTraining/react-router/issues/4683
  // eslint-disable-next-line react/prop-types
  staticContext,
  ...otherProps
}) => (
  <button
    type="button"
    className={`back-button ${className}`}
    onClick={history.goBack}
    {...otherProps}
  >
    <Icon svg="ico-back-simple-w" alt="Retour" />
  </button>
)

BackButton.defaultProps = {
  className: '',
}

BackButton.propTypes = {
  className: PropTypes.string,
  history: PropTypes.object.isRequired,
  location: PropTypes.object.isRequired,
  match: PropTypes.object.isRequired,
}

export default compose(withRouter)(BackButton)
