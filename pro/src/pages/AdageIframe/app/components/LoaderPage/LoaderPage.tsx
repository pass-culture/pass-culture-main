import './LoaderPage.scss'
import * as React from 'react'

import { Spinner } from 'ui-kit/Spinner/Spinner'

export const LoaderPage = (): JSX.Element => (
  <div className="root-adage">
    <main className="loader-page" id="content">
      {' '}
      <Spinner />
    </main>
  </div>
)
