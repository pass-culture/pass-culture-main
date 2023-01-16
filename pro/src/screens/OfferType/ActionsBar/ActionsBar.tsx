import React from 'react'

import ActionsBarSticky from 'components/ActionsBarSticky'
import { computeOffersUrl } from 'core/Offers/utils'
import { ReactComponent as IcoMiniArrowRight } from 'icons/ico-mini-arrow-right.svg'
import { Button, ButtonLink } from 'ui-kit'
import { ButtonVariant, IconPositionEnum } from 'ui-kit/Button/types'

interface IActionsBar {
  getNextPageHref: () => void
  disableNextButton?: boolean
}

const ActionsBar = ({
  getNextPageHref,
  disableNextButton = false,
}: IActionsBar): JSX.Element => {
  return (
    <ActionsBarSticky>
      <ActionsBarSticky.Left>
        <ButtonLink
          link={{ to: computeOffersUrl({}), isExternal: false }}
          variant={ButtonVariant.SECONDARY}
        >
          Annuler et quitter
        </ButtonLink>
      </ActionsBarSticky.Left>
      <ActionsBarSticky.Right>
        <Button
          onClick={getNextPageHref}
          Icon={IcoMiniArrowRight}
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
