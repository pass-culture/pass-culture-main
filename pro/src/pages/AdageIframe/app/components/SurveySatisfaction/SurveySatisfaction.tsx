import cn from 'classnames'
import React, { useState } from 'react'

import strokeCloseIcon from 'icons/stroke-close.svg'
import { Button, ButtonLink } from 'ui-kit'
import { ButtonVariant } from 'ui-kit/Button/types'
import { SvgIcon } from 'ui-kit/SvgIcon/SvgIcon'

import styles from './SurveySatisfaction.module.scss'

const LOCAL_STORAGE_HAS_SEEN_SATISFACTION_KEY = 'SURVEY_SATISFACTION_ADAGE_SEEN'

export const SurveySatisfaction = (): JSX.Element => {
  const [shouldHideSurveySatisfaction, setShouldHideSurveySatisfaction] =
    useState(
      Boolean(localStorage.getItem(LOCAL_STORAGE_HAS_SEEN_SATISFACTION_KEY))
    )

  const onCloseSurvey = () => {
    localStorage.setItem(LOCAL_STORAGE_HAS_SEEN_SATISFACTION_KEY, 'true')
    setShouldHideSurveySatisfaction(true)
  }

  return !shouldHideSurveySatisfaction ? (
    <div
      className={cn(styles['survey-satisfaction'], {
        [styles['survey-satisfaction-closed']]: shouldHideSurveySatisfaction,
      })}
    >
      <div className={styles['survey-close']}>
        <button
          onClick={onCloseSurvey}
          title="Masquer le bandeau"
          type="button"
          className={styles['survey-close-button']}
        >
          <SvgIcon
            src={strokeCloseIcon}
            alt=""
            className={styles['survey-close-icon']}
          />
        </button>
      </div>

      <div className={styles['survey-satisfaction-infos']}>
        <div className={styles['survey-title']}>Enquête de satisfaction</div>
        <div className={styles['survey-description']}>
          Le pass Culture souhaite recueillir votre avis sur cette page web :
          Les offres pass Culture.
          <br /> Cela ne vous prendra que 2 minutes.
        </div>

        <div>
          <Button
            className={styles['survey-button-secondary']}
            onClick={onCloseSurvey}
          >
            J’ai déjà répondu
          </Button>

          <ButtonLink
            variant={ButtonVariant.PRIMARY}
            link={{
              to: 'https://passculture.qualtrics.com/jfe2/preview/previewId/b9b1d8ad-c0c2-45ba-9e55-fd562da0e798/SV_8w5mdHmrxly9bcW?Q_CHL=preview&Q_SurveyVersionID=current',
              isExternal: true,
              rel: 'noopener noreferrer',
              target: '_blank',
            }}
            className={styles['survey-button']}
          >
            Je donne mon avis
          </ButtonLink>
        </div>
      </div>
    </div>
  ) : (
    <div></div>
  )
}
