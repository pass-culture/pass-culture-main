import React from 'react'

import OfferersList from '../OfferersList'
import withLogin from '../hocs/withLogin'
import PageWrapper from '../layout/PageWrapper'
import SignoutButton from '../layout/SignoutButton'

const OfferersPage = ({ user }) => {
  return [
    <PageWrapper key={0} name="profile">
      <p className="title">
        <strong>Vos espaces</strong>
      </p>
      <OfferersList />
    </PageWrapper>,
  ]
}

export default withLogin({ isRequired: true })(OfferersPage)
