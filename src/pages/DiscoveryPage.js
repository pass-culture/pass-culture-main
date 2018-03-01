import React from 'react'

import UserMediationsExplorer from '../components/UserMediationsExplorer'
import withLogin from '../hocs/withLogin'

const DiscoveryPage = () => {
  return (
    <main className='page discovery-page center'>
      <UserMediationsExplorer />
    </main>
  )
}

export default withLogin({ isRequired: true })(DiscoveryPage)
