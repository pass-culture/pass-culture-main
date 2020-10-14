import classnames from 'classnames'
import PropTypes from 'prop-types'
import React from 'react'

const ActionsBar = ({ isVisible, children }) => {
  return (
    <div className={classnames('actions-bar', { 'actions-bar-visible': isVisible })}>
      <div className="container">
        <div className="actions-bar-content">
          {children}
        </div>
      </div>
    </div>
  )
}

ActionsBar.defaultProps = {
  isVisible: false,
}

ActionsBar.propTypes = {
  children: PropTypes.shape().isRequired,
  isVisible: PropTypes.bool,
}

export default ActionsBar
