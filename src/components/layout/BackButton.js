import PropTypes from 'prop-types'
import { Icon } from 'pass-culture-shared'
import React from 'react'
import { withRouter } from 'react-router'
import { compose } from 'redux'

const BackButton = ({ history, match, location, className, ...otherProps }) => (
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
  match: PropTypes.object.isRequired,
  location: PropTypes.object.isRequired,
}

export default compose(withRouter)(BackButton)
