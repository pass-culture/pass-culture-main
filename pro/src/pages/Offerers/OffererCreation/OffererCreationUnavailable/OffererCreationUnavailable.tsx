import React, { FunctionComponent } from 'react'

import strokeWipIcon from 'icons/stroke-wip.svg'
import { SvgIcon } from 'ui-kit/SvgIcon/SvgIcon'

import styles from './OffererCreationUnavailable.module.scss'

export const OffererCreationUnavailable: FunctionComponent = () => {
  return (
    <div className={styles['unavailable-offerer-creation']}>
      <SvgIcon
        alt=""
        src={strokeWipIcon}
        className={styles['unavailable-offerer-creation-icon']}
      />
      <h2 className={styles['heading-2']}>
        Impossibilité de créer une structure actuellement.
      </h2>
      <h3>Merci de réessayer ultérieurement.</h3>
    </div>
  )
}
