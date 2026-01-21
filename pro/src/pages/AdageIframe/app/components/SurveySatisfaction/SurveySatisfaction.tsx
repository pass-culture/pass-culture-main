import cn from 'classnames'
import { useState } from 'react'

import { apiAdage } from '@/apiClient/api'
import { useSnackBar } from '@/commons/hooks/useSnackBar'
import { Button } from '@/design-system/Button/Button'
import { ButtonVariant } from '@/design-system/Button/types'
import fullLinkIcon from '@/icons/full-link.svg'
import strokeCloseIcon from '@/icons/stroke-close.svg'
import { SvgIcon } from '@/ui-kit/SvgIcon/SvgIcon'

import styles from './SurveySatisfaction.module.scss'

interface SurveySatisfactionProps {
  queryId?: string
}

export const SurveySatisfaction = ({
  queryId,
}: SurveySatisfactionProps): JSX.Element => {
  const [shouldHideSurveySatisfaction, setShouldHideSurveySatisfaction] =
    useState(false)

  const snackBar = useSnackBar()

  const onCloseSurvey = async () => {
    try {
      await apiAdage.saveRedactorPreferences({
        feedback_form_closed: true,
      })
      setShouldHideSurveySatisfaction(true)
    } catch {
      snackBar.error('Une erreur est survenue. Merci de réessayer plus tard')
    }
  }

  const logOpenSatisfactionSurvey = () => {
    apiAdage.logOpenSatisfactionSurvey({
      iframeFrom: location.pathname,
      queryId: queryId,
    })
  }

  return !shouldHideSurveySatisfaction ? (
    <div
      className={cn(styles['survey-satisfaction'], {
        [styles['survey-satisfaction-closed']]: shouldHideSurveySatisfaction,
      })}
    >
      <div className={styles['survey-satisfaction-infos']}>
        <div className={styles['survey-satisfaction-infos-head']}>
          <div className={styles['survey-title']}>Enquête de satisfaction</div>
          <button
            onClick={onCloseSurvey}
            type="button"
            className={styles['survey-close']}
          >
            <SvgIcon
              src={strokeCloseIcon}
              alt="Masquer le bandeau"
              width="24"
            />
          </button>
        </div>
        <div className={styles['survey-description']}>
          Le pass Culture souhaite recueillir votre avis sur cette page web :
          Les offres pass Culture.
          <br /> Cela ne vous prendra que 2 minutes.
        </div>

        <div className={styles['survey-actions']}>
          <Button
            onClick={onCloseSurvey}
            variant={ButtonVariant.SECONDARY}
            label="J'ai déjà répondu"
          />

          <Button
            as="a"
            variant={ButtonVariant.PRIMARY}
            to="https://passculture.qualtrics.com/jfe/form/SV_8w5mdHmrxly9bcW"
            isExternal
            opensInNewTab
            icon={fullLinkIcon}
            onClick={logOpenSatisfactionSurvey}
            label="Je donne mon avis"
          />
        </div>
      </div>
    </div>
  ) : (
    <div />
  )
}
