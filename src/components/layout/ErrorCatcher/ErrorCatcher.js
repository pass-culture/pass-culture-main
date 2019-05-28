/* eslint
  react/jsx-one-expression-per-line: 0 */
import PropTypes from 'prop-types'
import React, { PureComponent } from 'react'

import logger from '../../../utils/logger'

class ErrorCatcher extends PureComponent {
  constructor(props) {
    super(props)
    this.state = { hasError: false }
  }

  static getDerivedStateFromError() {
    return { hasError: true }
  }

  componentDidCatch(error, info) {
    // https://reactjs.org/blog/2017/07/26/error-handling-in-react-16.html
    logger.log(`Current react version: ${React.version}`)
    logger.error(`Error: ${error}`)
    logger.error(`With info: ${JSON.stringify(info)}`)
  }

  render() {
    const { hasError } = this.state
    const { children, history } = this.props
    if (!hasError) return children
    return (
      <div id="error-catcher">
        <div className="flex-1 flex-rows flex-center">
          <h2 className="fs20">Une erreur est survenue.</h2>
          <p className="mt12">
            <button
              className="no-background border-all rd4 py12 px18 is-inline-block is-white-text text-center fs16"
              onClick={() => {
                history.replace('/decouverte')
                window.location.reload()
              }}
              type="button"
            >
              <span>Retour aux offres</span>
            </button>
          </p>
        </div>
      </div>
    )
  }
}

ErrorCatcher.propTypes = {
  children: PropTypes.node.isRequired,
  history: PropTypes.object.isRequired,
}

export default ErrorCatcher
