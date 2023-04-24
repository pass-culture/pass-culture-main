import './UnauthenticatedError.scss'
import * as React from 'react'

export const UnauthenticatedError = (): JSX.Element => {
  return (
    <main className="error" id="content">
      <h1>Une erreur s’est produite.</h1>
      <div>
        Contactez{' '}
        <a href="mailto:adage-pass-culture@education.gouv.fr">
          adage-pass-culture@education.gouv.fr
        </a>{' '}
        pour obtenir de l’aide.
      </div>
    </main>
  )
}
