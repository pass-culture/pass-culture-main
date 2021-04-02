import React from 'react'

import Icon from 'components/layout/Icon'
import PageTitle from 'components/layout/PageTitle/PageTitle'

const Unavailable = () => {
  return (
    <main className=" fullscreen unavailable-page">
      <div className="u-main">
        <PageTitle title="Page indisponible" />
        <Icon svg="ico-unavailable-page" />
        <h1>
          {'Page indisponible'}
        </h1>
        <p>
          {'Veuillez rééssayer plus tard'}
        </p>
      </div>
      <Icon svg="logo-pass-culture" />
    </main>
  )
}

export default Unavailable
