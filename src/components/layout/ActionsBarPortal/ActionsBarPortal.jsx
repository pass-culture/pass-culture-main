import classnames from 'classnames'
import PropTypes from 'prop-types'
import React from 'react'

import PortalContainer from 'app/PortalContainer'

const ActionsBarPortal = ({ isVisible, children }) => (
  <PortalContainer>
    <div
      className={classnames('actions-bar', { 'actions-bar-visible': isVisible })}
      data-testid="actions-bar"
    >
      <div className="container">
        <div className="actions-bar-content">
          {children}
        </div>
      </div>
    </div>
  </PortalContainer>
)

ActionsBarPortal.defaultProps = {
  isVisible: false,
}

ActionsBarPortal.propTypes = {
  children: PropTypes.shape().isRequired,
  isVisible: PropTypes.bool,
}

export default ActionsBarPortal
