import cn from 'classnames'
import { useState } from 'react'

import { apiAdage } from 'apiClient/api'
import { useNotification } from 'hooks/useNotification'
import fullLinkIcon from 'icons/full-link.svg'
import strokeCloseIcon from 'icons/stroke-close.svg'
import { Button } from 'ui-kit/Button/Button'
import { ButtonLink } from 'ui-kit/Button/ButtonLink'
import { ButtonVariant } from 'ui-kit/Button/types'
import { SvgIcon } from 'ui-kit/SvgIcon/SvgIcon'

import styles from './SurveySatisfaction.module.scss'

interface SurveySatisfactionProps {
  queryId?: string
}

export const SurveySatisfaction = ({
  queryId,
}: SurveySatisfactionProps): JSX.Element => {
  const [shouldHideSurveySatisfaction, setShouldHideSurveySatisfaction] =
    useState(false)

  const notify = useNotification()

  const onCloseSurvey = async () => {
    try {
      await apiAdage.saveRedactorPreferences({
        feedback_form_closed: true,
      })
      setShouldHideSurveySatisfaction(true)
    } catch {
      notify.error('Une erreur est survenue. Merci de réessayer plus tard')
    }
  }

  const logOpenSatisfactionSurvey = () => {
    // eslint-disable-next-line @typescript-eslint/no-floating-promises
    apiAdage.logOpenSatisfactionSurvey({
      iframeFrom: location.pathname,
      queryId: queryId,
    })
  }

  return !shouldHideSurveySatisfaction ? (
    <div
      className={cn(styles['survey-satisfaction'], {
        [styles['survey-satisfaction-closed'] ?? '']:
          shouldHideSurveySatisfaction,
      })}
    >
      <div className={styles['survey-satisfaction-infos']}>
        <div className={styles['survey-satisfaction-infos-head']}>
          <div className={styles['survey-title']}>Enquête de satisfaction</div>
          <button
            onClick={onCloseSurvey}
            title="Masquer le bandeau"
            type="button"
            className={styles['survey-close']}
          >
            <SvgIcon src={strokeCloseIcon} alt="" width="24" />
          </button>
        </div>
        <div className={styles['survey-description']}>
          Le pass Culture souhaite recueillir votre avis sur cette page web :
          Les offres pass Culture.
          <br /> Cela ne vous prendra que 2 minutes.
        </div>

        <div className={styles['survey-actions']}>
          <Button
            className={styles['survey-button-secondary']}
            onClick={onCloseSurvey}
          >
            J’ai déjà répondu
          </Button>

          <ButtonLink
            variant={ButtonVariant.PRIMARY}
            to="https://passculture.qualtrics.com/jfe/form/SV_8w5mdHmrxly9bcW"
            isExternal
            opensInNewTab
            icon={fullLinkIcon}
            className={styles['survey-button']}
            onClick={logOpenSatisfactionSurvey}
          >
            Je donne mon avis
          </ButtonLink>
        </div>
      </div>
    </div>
  ) : (
    <div />
  )
}
