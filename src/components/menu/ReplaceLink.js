import React from 'react'
import PropTypes from 'prop-types'
import { withRouter } from 'react-router-dom'

class ReplaceLink extends React.PureComponent {
  navigate() {
    const { disabled, history, onClick, to } = this.props
    if (!disabled) {
      if (onClick) {
        onClick()
      }
      history.replace(to)
    }
  }

  render() {
    const { children, className, disabled } = this.props

    return (
      <div
        disabled={disabled}
        className={`${className} pointer`}
        onKeyPress={() => this.navigate()}
        onClick={() => this.navigate()}
        role="menuitem"
        tabIndex={0}
      >
        {children}
      </div>
    )
  }
}

ReplaceLink.defaultProps = {
  className: '',
  disabled: false,
  onClick: null,
}

ReplaceLink.propTypes = {
  children: PropTypes.object.isRequired,
  className: PropTypes.string,
  disabled: PropTypes.bool,
  history: PropTypes.object.isRequired,
  onClick: PropTypes.func,
  to: PropTypes.string.isRequired,
}

export default withRouter(ReplaceLink)
