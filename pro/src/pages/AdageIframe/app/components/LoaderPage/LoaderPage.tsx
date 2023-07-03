import './LoaderPage.scss'
import * as React from 'react'

import { ReactComponent as Logo } from 'icons/logo-pass-culture-dark.svg'
import Spinner from 'ui-kit/Spinner/Spinner'

export const LoaderPage = (): JSX.Element => (
  <div className="root-adage">
    <header>
      <Logo />
    </header>
    <main className="loader-page" id="content">
      {' '}
      <Spinner />
    </main>
  </div>
)
