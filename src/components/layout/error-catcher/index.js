/* eslint
  react/jsx-one-expression-per-line: 0 */
import React from 'react'
import PropTypes from 'prop-types'
import { Logger } from 'pass-culture-shared'
import { withRouter } from 'react-router-dom'

import ErrorCatcherView from './ErrorCatcherView'

export class RawErrorCatcher extends React.PureComponent {
  static getDerivedStateFromError() {
    return { hasError: true }
  }

  constructor(props) {
    super(props)
    this.state = { hasError: false }
  }

  componentDidCatch(error, info) {
    // https://reactjs.org/blog/2017/07/26/error-handling-in-react-16.html
    Logger.log(`Current react version: ${React.version}`)
    Logger.error(`Error: ${error}`)
    Logger.error(`With info: ${JSON.stringify(info)}`)
  }

  render() {
    const { hasError } = this.state
    const { children, history } = this.props
    if (!hasError) return children
    return (
      <ErrorCatcherView
        onClick={() => {
          history.replace('/decouverte')
          window.location.reload()
        }}
      />
    )
  }
}

RawErrorCatcher.propTypes = {
  children: PropTypes.node.isRequired,
  history: PropTypes.object.isRequired,
}

export default withRouter(RawErrorCatcher)
