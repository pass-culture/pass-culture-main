import classnames from 'classnames'
import PropTypes from 'prop-types'
import React from 'react'
import { withRouter } from 'react-router'
import { compose } from 'redux'

import { Icon } from './Icon'

const BackButton = ({ className, history, ...otherProps }) => {
  return (
    <button
      className={classnames('back-button', className)}
      onClick={history.goBack}
      type="button"
      {...otherProps}
    >
      <Icon svg="ico-back-simple-w" />
    </button>
  )
}

BackButton.propTypes = {
  className: PropTypes.string.isRequired,
  history: PropTypes.shape().isRequired,
}

export default compose(withRouter)(BackButton)
