import React from 'react'

import withLogin from '../hocs/withLogin'
import PageWrapper from '../layout/PageWrapper'
import SignoutButton from '../layout/SignoutButton'

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
