import React from 'react'

import withLogin from '../hocs/withLogin'
import PageWrapper from '../layout/PageWrapper'
import HomeCard from '../HomeCard'

const HomePage = ({ user }) => {
  return (
    <PageWrapper name='home' whiteHeader>
      <div className='home-cards columns'>
        <HomeCard svg='ico-guichet-w' title='Guichet' text="Enregistrez les codes de réservation des porteurs du Pass (en construction, pas encore disponible)." navLink='/guichet' />
        <HomeCard svg='ico-offres-w' title='Vos offres' text='Créez et mettez en avant vos offres présentes sur le Pass.' navLink='/offres' />
      </div>
    </PageWrapper>
  )
}

export default withLogin({ isRequired: true })(HomePage)
