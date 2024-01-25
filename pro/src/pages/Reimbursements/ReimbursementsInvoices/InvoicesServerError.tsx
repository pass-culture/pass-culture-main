import React from 'react'

import strokeWipIcon from 'icons/stroke-wip.svg'
import { SvgIcon } from 'ui-kit/SvgIcon/SvgIcon'

import styles from './InvoicesNoResult.module.scss'

const InvoicesServerError = (): JSX.Element => {
  return (
    <div className={styles['no-refunds']}>
      <SvgIcon
        alt=""
        src={strokeWipIcon}
        className={styles['no-refunds-icon']}
        viewBox="0 0 200 156"
        width="130"
      />
      <p className={styles['no-refunds-title']}>Une erreur est survenue</p>
      <p>Veuillez réessayer plus tard</p>
    </div>
  )
}

export default InvoicesServerError
