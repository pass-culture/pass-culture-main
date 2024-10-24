import React from 'react'

import { useAnalytics } from 'app/App/analytics/firebase'
import { Events } from 'commons/core/FirebaseEvents/constants'
import { computeIndividualOffersUrl } from 'commons/core/Offers/utils/computeIndividualOffersUrl'
import { ActionsBarSticky } from 'components/ActionsBarSticky/ActionsBarSticky'
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
  const { logEvent } = useAnalytics()

  return (
    <ActionsBarSticky>
      <ActionsBarSticky.Left>
        <ButtonLink
          to={computeIndividualOffersUrl({})}
          variant={ButtonVariant.SECONDARY}
          onClick={() => logEvent(Events.CLICKED_CANCEL_OFFER_CREATION)}
        >
          Annuler et quitter
        </ButtonLink>
      </ActionsBarSticky.Left>
      <ActionsBarSticky.Right>
        <Button
          type="submit"
          icon={fullRightIcon}
          iconPosition={IconPositionEnum.RIGHT}
          disabled={disableNextButton}
        >
          Étape suivante
        </Button>
      </ActionsBarSticky.Right>
    </ActionsBarSticky>
  )
}
