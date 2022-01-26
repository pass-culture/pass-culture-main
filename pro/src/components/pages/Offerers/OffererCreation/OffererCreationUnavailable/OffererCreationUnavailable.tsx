import React, { FunctionComponent } from 'react'

import { ReactComponent as UnavailableIcon } from 'icons/ico-unavailable-gradient.svg'

import styles from './OffererCreationUnavailable.module.scss'

const OffererCreationUnavailable: FunctionComponent = () => {
  return (
    <div className={styles['unavailable-offerer-creation']}>
      <UnavailableIcon />
      <h2 className={styles['heading-2']}>
        Impossibilité de créer une structure actuellement.
      </h2>
      <h3>Merci de réessayer ultérieurement.</h3>
    </div>
  )
}

export default OffererCreationUnavailable
