import React from 'react'
import { useTranslation } from 'react-i18next'

import { useAnalytics } from 'app/App/analytics/firebase'
import { ActionsBarSticky } from 'components/ActionsBarSticky/ActionsBarSticky'
import { Events } from 'core/FirebaseEvents/constants'
import { computeIndividualOffersUrl } from 'core/Offers/utils/computeIndividualOffersUrl'
import fullRightIcon from 'icons/full-right.svg'
import { Button } from 'ui-kit/Button/Button'
import { ButtonLink } from 'ui-kit/Button/ButtonLink'
import { ButtonVariant, IconPositionEnum } from 'ui-kit/Button/types'

interface ActionsBarProps {
  disableNextButton?: boolean
}

export const ActionsBar = ({
  disableNextButton = false,
}: ActionsBarProps): JSX.Element => {
  const { t } = useTranslation('common')
  const { logEvent } = useAnalytics()

  return (
    <ActionsBarSticky>
      <ActionsBarSticky.Left>
        <ButtonLink
          to={computeIndividualOffersUrl({})}
          variant={ButtonVariant.SECONDARY}
          onClick={() => logEvent(Events.CLICKED_CANCEL_OFFER_CREATION)}
        >
          {t('cancel_and_quit')}
        </ButtonLink>
      </ActionsBarSticky.Left>
      <ActionsBarSticky.Right>
        <Button
          type="submit"
          icon={fullRightIcon}
          iconPosition={IconPositionEnum.RIGHT}
          disabled={disableNextButton}
        >
          {t('next_step')}
        </Button>
      </ActionsBarSticky.Right>
    </ActionsBarSticky>
  )
}
