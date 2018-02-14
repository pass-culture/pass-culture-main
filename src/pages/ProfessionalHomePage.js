import React from 'react'

import OffersList from '../components/OffersList'
import OfferNewButton from '../components/OfferNewButton'
import SearchInput from '../components/SearchInput'

const ProfessionalHomePage = () => {
  return (
    <main className='professional-home-page p2'>
      <div className='flex items-center flex-start mt2'>
        <OfferNewButton />
        <SearchInput />
      </div>
      <OffersList />
    </main>
  )
}

export default ProfessionalHomePage
