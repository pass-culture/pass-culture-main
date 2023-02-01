import React from 'react'

import PageTitle from 'components/PageTitle/PageTitle'
import Icon from 'ui-kit/Icon/Icon'

const Unavailable = () => {
  return (
    <main className=" fullscreen unavailable-page">
      <PageTitle title="Page indisponible" />
      <Icon className="error-icon" svg="ico-unavailable-page-white" />
      <h1>Page indisponible</h1>
      <p>Veuillez rééssayer plus tard</p>
      <Icon className="brand-logo" svg="logo-pass-culture" />
    </main>
  )
}

export default Unavailable
