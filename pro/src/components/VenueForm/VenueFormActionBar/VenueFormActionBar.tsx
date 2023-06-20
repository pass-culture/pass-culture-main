import { useFormikContext } from 'formik'
import React from 'react'

import ActionsBarSticky from 'components/ActionsBarSticky'
import FormLayout from 'components/FormLayout'
import useCurrentUser from 'hooks/useCurrentUser'
import { ButtonLink, SubmitButton } from 'ui-kit'
import { ButtonVariant } from 'ui-kit/Button/types'

import { VenueFormValues } from '../types'

interface VenueFormActionBarProps {
  offererId: number
  isCreatingVenue: boolean
}

const VenueFormActionBar = ({
  offererId,
  isCreatingVenue,
}: VenueFormActionBarProps) => {
  const { currentUser } = useCurrentUser()
  const { isSubmitting } = useFormikContext<VenueFormValues>()

  return (
    <FormLayout.Actions>
      <ActionsBarSticky>
        <ActionsBarSticky.Left>
          <ButtonLink
            variant={ButtonVariant.SECONDARY}
            link={{
              to: currentUser.isAdmin ? `/structures/${offererId}` : '/accueil',
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
    </FormLayout.Actions>
  )
}

export default VenueFormActionBar
