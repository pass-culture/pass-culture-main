import React from 'react'

import UserMediationsDeck from '../components/UserMediationsDeck'
import withLogin from '../hocs/withLogin'

const DiscoveryPage = () => {
  return (
    <main className='page discovery-page center'>
      <UserMediationsDeck />
    </main>
  )
}

export default withLogin({ isRequired: true })(DiscoveryPage)
