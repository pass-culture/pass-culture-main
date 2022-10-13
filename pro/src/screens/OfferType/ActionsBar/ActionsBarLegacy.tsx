import React from 'react'

import { computeOffersUrl } from 'core/Offers/utils'
import FormLayout from 'new_components/FormLayout'
import { Button, ButtonLink } from 'ui-kit'
import { ButtonVariant } from 'ui-kit/Button/types'

interface IActionsBarLegacy {
  getNextPageHref: () => void
}

const ActionsBarLegacy = ({
  getNextPageHref,
}: IActionsBarLegacy): JSX.Element => {
  return (
    <FormLayout.Actions>
      <ButtonLink
        link={{ to: computeOffersUrl({}), isExternal: false }}
        variant={ButtonVariant.SECONDARY}
      >
        Retour
      </ButtonLink>
      <Button onClick={getNextPageHref}>Étape suivante</Button>
    </FormLayout.Actions>
  )
}

export default ActionsBarLegacy
