import React from 'react'

import { ROOT_PATH } from 'utils/config'

const Unavailable = () => {
  return (
    <main className="page fullscreen unavailable-page">
      <div className="error-message">
        <img
          alt=""
          src={`${ROOT_PATH}/icons/ico-unavailable-page.svg`}
        />
        <h1>
          {'Page indisponible'}
        </h1>
        <p>
          {'Veuillez rééssayer plus tard'}
        </p>
      </div>

      <div className="passculture-logo">
        <img
          alt=""
          src={`${ROOT_PATH}/icon/app-icon-spotlight.svg`}
        />
      </div>
    </main>
  )
}

export default Unavailable
