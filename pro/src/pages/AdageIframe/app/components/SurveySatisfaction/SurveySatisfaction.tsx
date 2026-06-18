import { useState } from 'react'

import { apiAdage } from '@/apiClient/api'
import { useSnackBar } from '@/commons/hooks/useSnackBar'
import { VITE_ADAGE_SURVEY_SATISFACTION_URL } from '@/commons/utils/config'
import { Button } from '@/design-system/Button/Button'
import { ButtonVariant } from '@/design-system/Button/types'
import strokeCloseIcon from '@/icons/stroke-close.svg'
import { SvgIcon } from '@/ui-kit/SvgIcon/SvgIcon'

import styles from './SurveySatisfaction.module.scss'

interface SurveySatisfactionProps {
  onClose: () => void
  queryId?: string
}

export const SurveySatisfaction = ({
  onClose,
  queryId,
}: SurveySatisfactionProps) => {
  const [shouldHideSurveySatisfaction, setShouldHideSurveySatisfaction] =
    useState(false)

  const snackBar = useSnackBar()

  const onCloseSurvey = async () => {
    try {
      await apiAdage.saveRedactorPreferences({
        body: {
          feedback_form_closed: true,
        },
      })
      setShouldHideSurveySatisfaction(true)
      onClose()
    } catch {
      snackBar.error('Une erreur est survenue. Merci de réessayer plus tard')
    }
  }

  const logOpenSatisfactionSurvey = () => {
    apiAdage.logOpenSatisfactionSurvey({
      body: {
        iframeFrom: location.pathname,
        queryId,
      },
    })
  }

  if (shouldHideSurveySatisfaction) {
    return null
  }

  return (
    <div className={styles['survey-satisfaction']}>
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
          <p>
            Le pass Culture souhaite recueillir votre avis sur leur onglet dans
            ADAGE.
          </p>
          <p>Cela ne vous prendra que 5 minutes.</p>
        </div>

        <div className={styles['survey-actions']}>
          <Button
            onClick={onCloseSurvey}
            variant={ButtonVariant.SECONDARY}
            label="J’ai déjà répondu"
          />

          <Button
            as="a"
            variant={ButtonVariant.PRIMARY}
            to={VITE_ADAGE_SURVEY_SATISFACTION_URL}
            isExternal
            opensInNewTab
            onClick={logOpenSatisfactionSurvey}
            label="Je donne mon avis"
          />
        </div>
      </div>
    </div>
  )
}
