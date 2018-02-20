import React from 'react'

import Explorer from '../components/Explorer'
import SearchInput from '../components/SearchInput'
import withLogin from '../hocs/withLogin'

const ClientHomePage = () => {
  return (
    <main className='page client-home-page center'>
      <SearchInput />
      <Explorer collectionName='userMediations' />
    </main>
  )
}

export default withLogin(ClientHomePage)
