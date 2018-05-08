import React, { Component } from 'react'
import { connect } from 'react-redux'
import { withRouter } from 'react-router'
import { compose } from 'redux'

import withLogin from '../hocs/withLogin'
import { requestData } from '../../reducers/data'
import PageWrapper from '../layout/PageWrapper'

class ProfilePage extends Component {

  render() {
    const { user } = this.props
    return (
      <PageWrapper
        name="profile"
        backButton
      >
        PROFILE
      </PageWrapper>
    )
  }
}

export default compose(
  withLogin({ isRequired: true })
)(ProfilePage)
