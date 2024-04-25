import React from 'react'

import { ActionsBarSticky } from 'components/ActionsBarSticky/ActionsBarSticky'
import { Events } from 'core/FirebaseEvents/constants'
import { computeOffersUrl } from 'core/Offers/utils'
import useAnalytics from 'hooks/useAnalytics'
import fullRightIcon from 'icons/full-right.svg'
import { Button } from 'ui-kit/Button/Button'
import { ButtonLink } from 'ui-kit/Button/ButtonLink'
import { ButtonVariant, IconPositionEnum } from 'ui-kit/Button/types'

interface ActionsBarProps {
  disableNextButton?: boolean
}

const ActionsBar = ({
  disableNextButton = false,
}: ActionsBarProps): JSX.Element => {
  const { logEvent } = useAnalytics()

  return (
    <ActionsBarSticky>
      <ActionsBarSticky.Left>
        <ButtonLink
          link={{ to: computeOffersUrl({}), isExternal: false }}
          variant={ButtonVariant.SECONDARY}
          onClick={() => logEvent?.(Events.CLICKED_CANCEL_OFFER_CREATION)}
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

export default ActionsBar
