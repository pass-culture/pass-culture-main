import React from 'react'

import Icon from 'components/layout/Icon'
import PageTitle from 'components/layout/PageTitle/PageTitle'

const Unavailable = () => {
  return (
    <main className=" fullscreen unavailable-page">
      <PageTitle title="Page indisponible" />
      <Icon className="error-icon" svg="ico-unavailable-page" />
      <h1>Page indisponible</h1>
      <p>Veuillez rééssayer plus tard</p>
      <Icon className="brand-logo" svg="logo-pass-culture" />
    </main>
  )
}

export default Unavailable
