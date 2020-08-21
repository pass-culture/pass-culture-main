import PropTypes from 'prop-types'
import React, { Component } from 'react'

import AnyError from './AnyError/AnyError'
import { ApiError } from './ApiError'
import GatewayTimeoutError from './GatewayTimeoutError/GatewayTimeoutError'

class ErrorsPage extends Component {
  static getDerivedStateFromError(error) {
    if (error instanceof ApiError) {
      return {
        httpCode: error.httpCode,
      }
    } else {
      throw error
    }
  }

  constructor(props) {
    super(props)

    this.state = {
      httpCode: false,
    }
  }

  render() {
    const { httpCode } = this.state
    const { children } = this.props

    if (!httpCode) return children

    if (httpCode === 504) {
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
