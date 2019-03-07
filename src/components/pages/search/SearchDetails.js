import React, { Component, Fragment } from 'react'
import { connect } from 'react-redux'
import { withRouter } from 'react-router-dom'
import { compose } from 'redux'

import Recto from '../../Recto'
import Verso from '../../verso'

class SearchDetails extends Component {
  constructor() {
    super()
    this.state = { forceDetailsVisible: false }
  }

  componentDidMount() {
    this.handleForceDetailsVisible()
  }

  handleForceDetailsVisible = () => {
    this.setState({ forceDetailsVisible: true })
  }

  render() {
    const { forceDetailsVisible } = this.state
    return (
      <Fragment>
        <Verso
          extraClassName="with-header"
          forceDetailsVisible={forceDetailsVisible}
        />
        <Recto
          areDetailsVisible={forceDetailsVisible}
          extraClassName="with-header"
          position="current"
        />
      </Fragment>
    )
  }
}

export default compose(
  withRouter,
  connect()
)(SearchDetails)
