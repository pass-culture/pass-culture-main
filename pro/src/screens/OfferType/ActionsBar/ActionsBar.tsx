import React from 'react'

import ActionsBarSticky from 'components/ActionsBarSticky'
import { Events } from 'core/FirebaseEvents/constants'
import { computeOffersUrl } from 'core/Offers/utils'
import useAnalytics from 'hooks/useAnalytics'
import IcoMiniArrowRight from 'icons/ico-mini-arrow-right.svg'
import { ButtonLink, SubmitButton } from 'ui-kit'
import { ButtonVariant, IconPositionEnum } from 'ui-kit/Button/types'

interface IActionsBar {
  disableNextButton?: boolean
}

const ActionsBar = ({
  disableNextButton = false,
}: IActionsBar): JSX.Element => {
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
        <SubmitButton
          Icon={IcoMiniArrowRight}
          iconPosition={IconPositionEnum.RIGHT}
          disabled={disableNextButton}
        >
          Étape suivante
        </SubmitButton>
      </ActionsBarSticky.Right>
    </ActionsBarSticky>
  )
}

export default ActionsBar
