import React from 'react'

import PageTitle from 'components/layout/PageTitle/PageTitle'

const Homepage = () => {
  return (
    <div className="homepage">
      <PageTitle title="Espace acteurs culturels" />
      <h1>
        {'Bienvenue dans l’espace acteurs culturels'}
      </h1>
      <h2>
        {'Structures'}
      </h2>
      <h2>
        {'Profil et aide'}
      </h2>
      <h2>
        {'Modalités d’usage'}
      </h2>
    </div>
  )
}

export default Homepage
