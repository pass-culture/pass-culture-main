import cn from 'classnames'
import { useState } from 'react'

import { storageAvailable } from '@/commons/utils/storageAvailable'
import fullClearIcon from '@/icons/full-clear.svg'
import { SvgIcon } from '@/ui-kit/SvgIcon/SvgIcon'

import styles from './HighlightBanner.module.scss'

interface HighlightBannerProps {
  title: string
  description: string
  localStorageKey: string
  img?: JSX.Element | string
  cta?: JSX.Element
}

export const HighlightBanner = ({
  title,
  description,
  localStorageKey,
  img,
  cta,
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
      className={cn(styles[`highlight-banner-adage`], {
        [styles[`highlight-banner-adage-closed`]]: shouldHideHighlightBanner,
      })}
    >
      <div className={styles[`container`]}>
        <div className={styles['title']}>{title}</div>
        <p className={styles['description']}>{description}</p>
        {cta}
      </div>
      {img && <div className={styles['img']}>{img}</div>}
      <button
        type="button"
        className={styles['close']}
        aria-label="Masquer le bandeau"
        onClick={onCloseHighlightBanner}
      >
        <SvgIcon src={fullClearIcon} alt="" width="24" />
      </button>
    </div>
  )
}
