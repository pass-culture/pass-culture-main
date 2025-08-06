import cn from 'classnames'
import { useState } from 'react'

import { storageAvailable } from '@/commons/utils/storageAvailable'
import fullClearIcon from '@/icons/full-clear.svg'
import strokeCloseIcon from '@/icons/stroke-close.svg'
import { Button } from '@/ui-kit/Button/Button'
import { ButtonVariant } from '@/ui-kit/Button/types'
import { SvgIcon } from '@/ui-kit/SvgIcon/SvgIcon'

import styles from './HighlightBanner.module.scss'

export enum HighlightBannerVariant {
  DEFAULT = 'default',
  ADAGE = 'adage',
}

const HighlightBannerCloseButton = ({
  variant,
  onClose,
}: {
  variant: HighlightBannerVariant
  onClose: React.MouseEventHandler<HTMLButtonElement>
}) => {
  return variant === HighlightBannerVariant.DEFAULT ? (
    <Button
      className={styles['close']}
      iconClassName={styles['close-svg']}
      variant={ButtonVariant.TERNARY}
      icon={strokeCloseIcon}
      aria-label="Fermer la bannière"
      onClick={onClose}
    />
  ) : (
    <button
      type="button"
      className={styles['close']}
      aria-label="Masquer le bandeau"
      onClick={onClose}
    >
      <SvgIcon src={fullClearIcon} alt="" width="24" />
    </button>
  )
}

interface HighlightBannerProps {
  title: string
  description: string
  localStorageKey: string
  img?: JSX.Element | string
  cta?: JSX.Element
  variant?: HighlightBannerVariant
}

export const HighlightBanner = ({
  title,
  description,
  localStorageKey,
  img,
  cta,
  variant = HighlightBannerVariant.DEFAULT,
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
      className={cn(styles[`highlight-banner-${variant}`], {
        [styles[`highlight-banner-${variant}-closed`]]:
          shouldHideHighlightBanner,
      })}
    >
      <div className={styles[`container`]}>
        <div className={styles['title']}>{title}</div>
        <p className={styles['description']}>{description}</p>
        {cta}
      </div>
      {img && <div className={styles['img']}>{img}</div>}
      <HighlightBannerCloseButton
        variant={variant}
        onClose={onCloseHighlightBanner}
      />
    </div>
  )
}
