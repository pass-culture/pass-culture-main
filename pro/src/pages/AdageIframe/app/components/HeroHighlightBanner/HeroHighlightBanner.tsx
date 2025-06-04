import cn from 'classnames'
import { useState } from 'react'

import fullNextIcon from 'icons/full-next.svg'
import StrokeCloseIcon from 'icons/stroke-close.svg'
import { Button } from 'ui-kit/Button/Button'
import { ButtonLink } from 'ui-kit/Button/ButtonLink'
import { ButtonVariant } from 'ui-kit/Button/types'

import styles from './HeroHighlightBanner.module.scss'
import imgHeadlineOffer from './image.png'

interface HeroHighlightBannerProps {
  title: string
  description: string
  localStorageKey: string
  img?: JSX.Element
  primaryButton?: JSX.Element
  secondaryButton?: JSX.Element
  queryId?: string
  redirectTo: string
}

export const HeroHighlightBanner = ({
  title,
  redirectTo,
  description,
}: HeroHighlightBannerProps) => {
  const [shouldHideHighlightBanner, setShouldHideHighlightBanner] =
    useState(true)

  const onCloseHighlightBanner = () => {
    setShouldHideHighlightBanner(false)
  }

  if (!shouldHideHighlightBanner) {
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
      </div>
      <img
        className={styles['highlight-banner-img']}
        alt=""
        src={imgHeadlineOffer}
        role="presentation"
      />
      <Button
        className={styles['highlight-banner-close']}
        variant={ButtonVariant.TERNARY}
        icon={StrokeCloseIcon}
        onClick={onCloseHighlightBanner}
      ></Button>
      <ButtonLink
        className={styles['highlight-banner-button']}
        variant={ButtonVariant.TERNARY}
        icon={fullNextIcon}
        to={redirectTo}
      >
        Créer une offre spéciale
      </ButtonLink>
    </div>
  )
}
