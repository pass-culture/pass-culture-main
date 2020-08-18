import React, { useCallback } from 'react'

import { ICONS_URL } from '../../../../../utils/config'

const AnyError = () => {
  const refreshPage = useCallback(() => window.location.reload(), [])

  return (
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
      <button
        className="ep-button"
        onClick={refreshPage}
        type="button"
      >
        {'Réessayer'}
      </button>
    </main>
  )
}

export default AnyError
