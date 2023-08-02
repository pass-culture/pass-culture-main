import cn from 'classnames'
import React, { useState } from 'react'

import fullClear from 'icons/full-clear.svg'
import { SvgIcon } from 'ui-kit/SvgIcon/SvgIcon'

import styles from './DiffuseHelp.module.scss'

const LOCAL_STORAGE_HAS_SEEN_DIFFUSE_HELP_KEY = 'DIFFUSE_HELP_ADAGE_SEEN'

export const DiffuseHelp = ({
  description,
}: {
  description: string
}): JSX.Element => {
  const [shouldHideDiffuseHelp, setShouldHideDiffuseHelp] = useState(
    Boolean(localStorage.getItem(LOCAL_STORAGE_HAS_SEEN_DIFFUSE_HELP_KEY))
  )

  const onCloseDiffuseHelp = () => {
    localStorage.setItem(LOCAL_STORAGE_HAS_SEEN_DIFFUSE_HELP_KEY, 'true')
    setShouldHideDiffuseHelp(true)
  }

  return !shouldHideDiffuseHelp ? (
    <div
      className={cn(styles['diffuse-help'], {
        [styles['diffuse-help-closed']]: shouldHideDiffuseHelp,
      })}
    >
      <div className={styles['diffuse-help-infos']}>
        <div className={styles['diffuse-help-container']}>
          <div className={styles['diffuse-help-title']}>Le saviez-vous ?</div>
          <div
            className={styles['diffuse-help-close']}
            onClick={onCloseDiffuseHelp}
            data-testid="close-diffuse-help"
          >
            <SvgIcon
              src={fullClear}
              alt=""
              className={styles['diffuse-help-close-icon']}
            />{' '}
          </div>
        </div>
        <div className={styles['diffuse-help-description']}>{description}</div>
      </div>
    </div>
  ) : (
    <div></div>
  )
}
