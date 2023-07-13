import './LoaderPage.scss'
import * as React from 'react'

import logoPassCultureIcon from 'icons/logo-pass-culture.svg'
import Spinner from 'ui-kit/Spinner/Spinner'
import { SvgIcon } from 'ui-kit/SvgIcon/SvgIcon'

export const LoaderPage = (): JSX.Element => (
  <div className="root-adage">
    <header>
      <SvgIcon src={logoPassCultureIcon} alt="" viewBox="0 0 71 24" />
    </header>
    <main className="loader-page" id="content">
      {' '}
      <Spinner />
    </main>
  </div>
)
