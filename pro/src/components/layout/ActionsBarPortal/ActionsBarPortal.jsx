import classnames from 'classnames'
import PropTypes from 'prop-types'
import React from 'react'

import PortalContainer from 'app/PortalContainer'

import style from './ActionsBarPortal.module.scss'

const ActionsBarPortal = ({ isVisible, children }) => (
  <PortalContainer>
    <div
      className={classnames(
        style['actions-bar'],
        isVisible && style['actions-bar-visible']
      )}
      data-testid="actions-bar"
    >
      <div className={style['actions-bar-content']}>{children}</div>
    </div>
  </PortalContainer>
)

ActionsBarPortal.defaultProps = {
  isVisible: false,
}

ActionsBarPortal.propTypes = {
  children: PropTypes.node.isRequired,
  isVisible: PropTypes.bool,
}

export default ActionsBarPortal
