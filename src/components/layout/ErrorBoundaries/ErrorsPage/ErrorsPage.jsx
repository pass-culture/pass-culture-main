import PropTypes from 'prop-types'
import React, { Component } from 'react'

import NotMatch from '../../../pages/not-match/NotMatch'
import { ApiError } from './ApiError'
import AnyError from './AnyError/AnyError'
import GatewayTimeoutError from './GatewayTimeoutError/GatewayTimeoutError'

class ErrorsPage extends Component {
  static getDerivedStateFromError() {
    return {
      hasError: true,
    }
  }

  constructor(props) {
    super(props)

    this.state = {
      hasError: false,
      httpCode: 0,
    }
  }

  componentDidCatch(error) {
    if (error instanceof ApiError) {
      this.setState({
        httpCode: error.httpCode,
      })
    }
  }

  render() {
    const { hasError, httpCode } = this.state
    const { children } = this.props

    if (!hasError) return children

    if (httpCode === 404) {
      return <NotMatch />
    } else if (httpCode === 504) {
      return <GatewayTimeoutError />
    } else {
      return <AnyError />
    }
  }
}

ErrorsPage.propTypes = {
  children: PropTypes.node.isRequired,
}

export default ErrorsPage
