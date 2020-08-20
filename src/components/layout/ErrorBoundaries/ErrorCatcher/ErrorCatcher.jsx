import PropTypes from 'prop-types'
import React, { PureComponent } from 'react'

class ErrorCatcher extends PureComponent {
  static getDerivedStateFromError() {
    return {
      hasError: true,
    }
  }

  constructor(props) {
    super(props)

    this.state = {
      hasError: false,
    }
  }

  render() {
    const { hasError } = this.state
    const { children } = this.props

    if (!hasError) return children

    return (
      <main className="ep-wrapper">
        <h1>
          {'Une erreur est survenue.'}
        </h1>
        <a
          className="ep-button"
          href="/"
        >
          {'Retour aux offres'}
        </a>
      </main>
    )
  }
}

ErrorCatcher.propTypes = {
  children: PropTypes.node.isRequired,
}

export default ErrorCatcher
