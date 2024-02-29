import { useFormikContext } from 'formik'
import React from 'react'

import ActionsBarSticky from 'components/ActionsBarSticky'
import { ButtonLink, SubmitButton } from 'ui-kit'
import { ButtonVariant } from 'ui-kit/Button/types'

import { VenueFormValues } from '../types'

interface VenueFormActionBarProps {
  isCreatingVenue: boolean
}

const VenueFormActionBar = ({ isCreatingVenue }: VenueFormActionBarProps) => {
  const { isSubmitting } = useFormikContext<VenueFormValues>()

  return (
    <ActionsBarSticky>
      <ActionsBarSticky.Left>
        <ButtonLink
          variant={ButtonVariant.SECONDARY}
          link={{
            to: '/accueil',
            isExternal: false,
          }}
        >
          Annuler et quitter
        </ButtonLink>
      </ActionsBarSticky.Left>
      <ActionsBarSticky.Right>
        <SubmitButton isLoading={isSubmitting}>
          Enregistrer et
          {isCreatingVenue ? ' créer le lieu' : ' quitter'}
        </SubmitButton>
      </ActionsBarSticky.Right>
    </ActionsBarSticky>
  )
}

export default VenueFormActionBar
