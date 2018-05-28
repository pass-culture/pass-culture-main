import React, { Component } from 'react'
import { connect } from 'react-redux'
import { compose } from 'redux'

import PageWrapper from '../layout/PageWrapper'
import withLogin from '../hocs/withLogin'

class AccoutingPage extends Component {
  render() {
    return (
      <PageWrapper name="accouting">
        VOTRE COMPTA
      </PageWrapper>
    )
  }
}

export default compose(
  withLogin({ isRequired: true })
)(AccoutingPage)
