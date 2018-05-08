import React, { Component } from 'react'
import { connect } from 'react-redux'
import { withRouter } from 'react-router'
import { compose } from 'redux'

import PageWrapper from '../layout/PageWrapper'
import { requestData } from '../../reducers/data'

class OfferPage extends Component {
  handleRequestData = () => {
    const {
      match: { params: { offerId } },
      requestData
    } = this.props
    requestData('GET', `offers?offerId=${offerId}`)
  }

  componentWillMount() {
    this.props.user && this.handleRequestData()
  }

  componentDidUpdate(prevProps) {
    const { user } = this.props
    if (user && user !== prevProps.user) {
      this.handleRequestData()
    }
  }

  render () {
    return (
      <PageWrapper name='offer'>
        OUAI
      </PageWrapper>
    )
  }
}

export default compose(
  withRouter,
  connect(
    state => ({}),
    { requestData }
  )
)(OfferPage)
