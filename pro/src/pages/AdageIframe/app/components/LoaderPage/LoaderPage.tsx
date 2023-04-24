import './LoaderPage.scss'
import * as React from 'react'

import { ReactComponent as Logo } from 'icons/logo-pass-culture-dark.svg'

import { Spinner } from '../Layout/Spinner/Spinner'

export const LoaderPage = (): JSX.Element => (
  <div className="root-adage">
    <header>
      <Logo />
    </header>
    <main className="loader-page" id="content">
      {' '}
      <Spinner message="Chargement en cours" />
    </main>
  </div>
)
