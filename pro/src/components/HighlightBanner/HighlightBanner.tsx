import cn from 'classnames'
import { useState } from 'react'

import {
  type LOCAL_STORAGE_KEY,
  localStorageManager,
} from '@/commons/utils/localStorageManager'
import fullClearIcon from '@/icons/full-clear.svg'
import { SvgIcon } from '@/ui-kit/SvgIcon/SvgIcon'

import styles from './HighlightBanner.module.scss'

interface HighlightBannerProps {
  title: string
  description: string
  localStorageKey: LOCAL_STORAGE_KEY
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
  // Without storage, the banner could not be dismissed for good: never show it.
  const [shouldHideHighlightBanner, setShouldHideHighlightBanner] = useState(
    () =>
      !localStorageManager.isAvailable() ||
      localStorageManager.getItem(localStorageKey) === 'true'
  )

  const onCloseHighlightBanner = () => {
    localStorageManager.setItem(localStorageKey, 'true')
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
        <p className={styles['title']}>{title}</p>
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
