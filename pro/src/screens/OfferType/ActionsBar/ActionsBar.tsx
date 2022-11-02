import React from 'react'

import { computeOffersUrl } from 'core/Offers/utils'
import { ReactComponent as IcoMiniArrowRight } from 'icons/ico-mini-arrow-right.svg'
import { ActionsBarSticky } from 'new_components/ActionsBarSticky'
import { Button, ButtonLink } from 'ui-kit'
import { ButtonVariant, IconPositionEnum } from 'ui-kit/Button/types'

interface IActionsBar {
  getNextPageHref: () => void
}

const ActionsBar = ({ getNextPageHref }: IActionsBar): JSX.Element => {
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
        >
          Étape suivante
        </Button>
      </ActionsBarSticky.Right>
    </ActionsBarSticky>
  )
}

export default ActionsBar
