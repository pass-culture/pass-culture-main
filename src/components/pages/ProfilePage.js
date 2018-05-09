import React from 'react'
import { connect } from 'react-redux'
import { withRouter } from 'react-router'
import { compose } from 'redux'

import withLogin from '../hocs/withLogin'
import PageWrapper from '../layout/PageWrapper'
import SignoutButton from '../layout/SignoutButton'
import { requestData } from '../../reducers/data'

const ProfilePage = ({ user }) => {
  return [
    <PageWrapper key={0} name="profile">
      TO DO
    </PageWrapper>,
    <section key={1} className="hero is-primary">
      <div className="hero-body">
        <div className="container">
          <SignoutButton />
        </div>
      </div>
    </section>
  ]
}

export default withLogin({ isRequired: true })(ProfilePage)
