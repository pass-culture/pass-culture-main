import { useFormikContext } from 'formik'
import React from 'react'

import { GetVenueResponseModel } from 'apiClient/v1'
import ActionsBarSticky from 'components/ActionsBarSticky'
import { ButtonLink, SubmitButton } from 'ui-kit'
import { ButtonVariant } from 'ui-kit/Button/types'

import { VenueCreationFormValues } from '../types'

export interface VenueFormActionBarProps {
  isCreatingVenue?: boolean
  venue?: GetVenueResponseModel
}

export const VenueFormActionBar = ({
  isCreatingVenue,
  venue,
}: VenueFormActionBarProps) => {
  const { isSubmitting } = useFormikContext<VenueCreationFormValues>()

  return (
    <ActionsBarSticky>
      <ActionsBarSticky.Left>
        <ButtonLink
          variant={ButtonVariant.SECONDARY}
          link={{
            to: isCreatingVenue
              ? '/accueil'
              : `/structures/${venue?.managingOfferer?.id}/lieux/${venue?.id}`,
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
