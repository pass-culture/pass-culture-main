import React from 'react'

import Explorer from '../components/Explorer'
import withLogin from '../hocs/withLogin'

const DiscoveryPage = () => {
  return (
    <main className='page discovery-page center'>
      <Explorer />
    </main>
  )
}

export default withLogin()(DiscoveryPage)
