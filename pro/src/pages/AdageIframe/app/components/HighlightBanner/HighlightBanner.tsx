import cn from 'classnames'
import { useState } from 'react'

import fullClearIcon from 'icons/full-clear.svg'
import { SvgIcon } from 'ui-kit/SvgIcon/SvgIcon'

import styles from './HighlightBanner.module.scss'
import { storageAvailable } from 'commons/utils/storageAvailable'


interface HighlightBannerProps {
  title: string
  description: string
  localStorageKey: string
  img?: JSX.Element
  primaryButton?: JSX.Element
  secondaryButton?: JSX.Element
  queryId?: string
}

export const HighlightBanner = ({
  title,
  description,
  localStorageKey,
  img,
  primaryButton,
  secondaryButton,
}: HighlightBannerProps) => {
  const isLocalStorageAvailable = storageAvailable('localStorage')
  const [shouldHideHighlightBanner, setShouldHideHighlightBanner] = useState(
    !isLocalStorageAvailable || Boolean(localStorage.getItem(localStorageKey))
  )

  const onCloseHighlightBanner = () => {
    localStorage.setItem(localStorageKey, 'true')
    setShouldHideHighlightBanner(true)
  }

  if (shouldHideHighlightBanner) { 
    return null
  }

  return (
    <div
      className={cn(styles['highlight-banner'], {
        [styles['highlight-banner-closed']]: shouldHideHighlightBanner,
      })}
    >
      <div className={styles['highlight-banner-container']}>
        <div className={styles['highlight-banner-title']}>{title}</div>
        <p className={styles['highlight-banner-description']}>{description}</p>
        {secondaryButton}
        {primaryButton}
      </div>
      {img && <div className={styles['highlight-banner-img']}>{img}</div>}
      <button
        onClick={onCloseHighlightBanner}
        aria-label="Masquer le bandeau"
        type="button"
        className={styles['highlight-banner-close']}
      >
        <SvgIcon src={fullClearIcon} alt="" width="24" />
      </button>
    </div>
  )
}
