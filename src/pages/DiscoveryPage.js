import React from 'react'

import Deck from '../components/Deck'
// import Deck from '../components/Deck'
import withLogin from '../hocs/withLogin'

const DiscoveryPage = () => {
  return (
    <main className='page discovery-page center'>
      <Deck />
    </main>
  )
}

export default withLogin({ isRequired: true })(DiscoveryPage)
