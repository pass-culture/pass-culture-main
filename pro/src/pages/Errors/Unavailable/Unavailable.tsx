import React from 'react'

import strokeWipIcon from 'icons/stroke-wip.svg'
import { SvgIcon } from 'ui-kit/SvgIcon/SvgIcon'

import styles from './Unavailable.module.scss'

const Unavailable = () => {
  return (
    <main className={styles['unavailable-page']} id="content">
      <SvgIcon
        className={styles['error-icon']}
        src={strokeWipIcon}
        alt=""
        viewBox="0 0 200 156"
      />
      <h1>Page indisponible</h1>
      <p>Veuillez rééssayer plus tard</p>
    </main>
  )
}

export default Unavailable
