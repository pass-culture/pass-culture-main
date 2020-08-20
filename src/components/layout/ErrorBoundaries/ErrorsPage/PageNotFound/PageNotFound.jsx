import React from 'react'
import { Link } from 'react-router-dom'

import { ICONS_URL } from '../../../../../utils/config'

const PageNotFound = () => (
  <main className="ep-wrapper">
    <img
      alt=""
      src={`${ICONS_URL}/404.svg`}
    />
    <h1>
      {'Oh non !'}
    </h1>
    <div className="ep-text-wrapper">
      {'Cette page n’existe pas.'}
    </div>
    <Link
      className="ep-button"
      to="/"
    >
      {'Retour'}
    </Link>
  </main>
)

export default PageNotFound
