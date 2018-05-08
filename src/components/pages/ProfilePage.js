import React from 'react'
import { withRouter } from 'react-router'

import withLogin from '../hocs/withLogin'
import { requestData } from '../../reducers/data'
import PageWrapper from '../layout/PageWrapper'

const ProfilePage = ({ user }) => {
  return (
    <PageWrapper name="profile">
      PROFILE
    </PageWrapper>
  )
}

export default withLogin({ isRequired: true })(ProfilePage)
