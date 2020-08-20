import React from 'react'

import { ICONS_URL } from '../../../../../utils/config'

const AnyError = () => (
  <main className="ep-wrapper">
    <img
      alt=""
      src={`${ICONS_URL}/ico-maintenance.svg`}
    />
    <h1>
      {'Oh non !'}
    </h1>
    <div className="ep-text-wrapper">
      <div>
        {'Une erreur s’est produite pendant'}
      </div>
      <div>
        {'le chargement de la page.'}
      </div>
    </div>
    <a
      className="ep-button"
      href={window.location.pathname}
    >
      {'Réessayer'}
    </a>
  </main>
)

export default AnyError
