import cn from 'classnames'
import { useState } from 'react'

import { useAnalytics } from 'app/App/analytics/firebase'
import { Events } from 'commons/core/FirebaseEvents/constants'
import { storageAvailable } from 'commons/utils/storageAvailable'
import { FormLayout } from 'components/FormLayout/FormLayout'
import fullThumbUpIcon from 'icons/full-thumb-up.svg'
import strokeValidIcon from 'icons/stroke-valid.svg'
import { Button } from 'ui-kit/Button/Button'
import { ButtonVariant } from 'ui-kit/Button/types'
import { SvgIcon } from 'ui-kit/SvgIcon/SvgIcon'

import styles from './HeadlineOfferVideoBanner.module.scss'

export const HeadlineOfferVideoBanner = () => {
  const [isGiven, setIsGiven] = useState<boolean>(
    storageAvailable('localStorage')
      ? Boolean(localStorage.getItem('LOCAL_STORAGE_HAS_GIVEN_VIDEO_OPINION'))
      : false
  )

  const [animate, setAnimate] = useState<boolean>(false) // Track animation state

  const { logEvent } = useAnalytics()

  const onClick = (opinion: string, answer: boolean) => {
    setAnimate(true)

    localStorage.setItem('LOCAL_STORAGE_HAS_GIVEN_VIDEO_OPINION', 'true')

    setIsGiven(
      Boolean(localStorage.getItem('LOCAL_STORAGE_HAS_GIVEN_VIDEO_OPINION'))
    )

    logEvent(opinion, {
      answer,
    })
  }

  return (
    <FormLayout.Section title="Vidéo">
      {isGiven ? (
        <div
          className={cn(
            styles['headline-offer-banner'],
            styles['headline-offer-opinion'],
            animate ? styles['fade-in'] : '' // Add animation class only when `animate` is true
          )}
          data-testid="awesome-banner"
        >
          <SvgIcon src={strokeValidIcon} alt="" width="48" />
          <p>Merci pour votre avis</p>
        </div>
      ) : (
        <div
          className={styles['headline-offer-banner']}
          data-testid="awesome-banner"
        >
          <p className={styles['headline-offer-title']}>
            <span aria-hidden="true">📹</span> Votre avis compte !
          </p>
          <p className={styles['headline-offer-description']}>
            L’ajout de vidéo arrive bientôt ! Seriez-vous intéressé.e pour en
            ajouter sur vos offres ?
          </p>
          <Button
            className={styles['headline-offer-button']}
            variant={ButtonVariant.TERNARY}
            icon={fullThumbUpIcon}
            onClick={() => onClick(Events.FAKE_DOOR_VIDEO_INTERESTED, true)}
          >
            Intéressé.e
          </Button>
          <Button
            className={styles['headline-offer-button']}
            iconClassName={styles['headline-offer-icon-down']}
            variant={ButtonVariant.TERNARY}
            icon={fullThumbUpIcon}
            onClick={() => onClick(Events.FAKE_DOOR_VIDEO_INTERESTED, false)}
          >
            Pas intéressé.e
          </Button>
        </div>
      )}
    </FormLayout.Section>
  )
}
