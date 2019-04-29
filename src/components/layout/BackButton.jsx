import classnames from 'classnames'
import React from 'react'
import { withRouter } from 'react-router'
import { compose } from 'redux'

import { Icon } from 'components/layout/Icon'

const BackButton = ({
  history,
  match,
  location,
  staticContext,
  className,
  ...otherProps
}) => {
  return (
    <button
      className={classnames('back-button', className)}
      onClick={history.goBack}
      {...otherProps}>
      <Icon svg="ico-back-simple-w" />
    </button>
  )
}

export default compose(withRouter)(BackButton)
