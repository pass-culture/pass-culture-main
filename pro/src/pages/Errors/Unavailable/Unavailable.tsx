import React from 'react'

import logoPassCultureIcon from 'icons/logo-pass-culture.svg'
import strokeWipIcon from 'icons/stroke-wip.svg'
import { SvgIcon } from 'ui-kit/SvgIcon/SvgIcon'

import styles from './Unavailable.module.scss'

const Unavailable = () => {
  return (
    <main className={`fullscreen ${styles['unavailable-page']}`} id="content">
      <SvgIcon
        className={styles['error-icon']}
        src={strokeWipIcon}
        alt=""
        viewBox="0 0 200 156"
      />
      <h1>Page indisponible</h1>
      <p>Veuillez rééssayer plus tard</p>
      <SvgIcon
        className={styles['brand-logo']}
        src={logoPassCultureIcon}
        alt=""
        viewBox="0 0 71 24"
      />
    </main>
  )
}

export default Unavailable
