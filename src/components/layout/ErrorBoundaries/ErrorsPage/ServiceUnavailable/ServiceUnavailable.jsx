import React from 'react'

import { ICONS_URL } from '../../../../../utils/config'

const ServiceUnavailable = () => (
  <main className="ep-wrapper">
    <img
      alt=""
      src={`${ICONS_URL}/logo-error.svg`}
    />
    <h1>
      {'Oops !'}
    </h1>
    <div className="ep-text-wrapper">
      <div>
        {'Une erreur s’est produite pendant'}
      </div>
      <div>
        {'le chargement des offres.'}
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

export default ServiceUnavailable
