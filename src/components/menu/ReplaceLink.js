import React from 'react'
import PropTypes from 'prop-types'
import { withRouter } from 'react-router-dom'

class ReplaceLink extends React.PureComponent {
  navigate() {
    const { history, onClick, to } = this.props
    if (onClick) {
      onClick()
    }
    history.replace(to)
  }

  render() {
    const { children, className } = this.props

    return (
      <div
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
  onClick: null,
}

ReplaceLink.propTypes = {
  children: PropTypes.object.isRequired,
  className: PropTypes.string,
  history: PropTypes.object.isRequired,
  onClick: PropTypes.func,
  to: PropTypes.string.isRequired,
}

export default withRouter(ReplaceLink)
