import React, { FunctionComponent } from 'react'

import strokeWipIcon from 'icons/stroke-wip.svg'
import { SvgIcon } from 'ui-kit/SvgIcon/SvgIcon'

import styles from './OffererCreationUnavailable.module.scss'

const OffererCreationUnavailable: FunctionComponent = () => {
  return (
    <div className={styles['unavailable-offerer-creation']}>
      <SvgIcon
        alt=""
        src={strokeWipIcon}
        viewBox="0 0 200 156"
        className={styles['unavailable-offerer-creation-icon']}
      />
      <h2 className={styles['heading-2']}>
        Impossibilité de créer une structure actuellement.
      </h2>
      <h3>Merci de réessayer ultérieurement.</h3>
    </div>
  )
}

export default OffererCreationUnavailable
