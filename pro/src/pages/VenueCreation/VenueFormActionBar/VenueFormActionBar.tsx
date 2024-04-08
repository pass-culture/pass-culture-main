import { useFormikContext } from 'formik'
import React from 'react'

import { GetVenueResponseModel } from 'apiClient/v1'
import { ButtonLink, SubmitButton } from 'ui-kit'
import { ButtonVariant } from 'ui-kit/Button/types'

import { VenueCreationFormValues } from '../types'

import styles from './VenueFormActionBar.module.scss'

export interface VenueFormActionBarProps {
  venue?: GetVenueResponseModel
}

export const VenueFormActionBar = ({ venue }: VenueFormActionBarProps) => {
  const { isSubmitting } = useFormikContext<VenueCreationFormValues>()

  return (
    <div className={styles['action-bar']}>
      <ButtonLink
        variant={ButtonVariant.SECONDARY}
        link={{
          to: `/structures/${venue?.managingOfferer.id}/lieux/${venue?.id}`,
          isExternal: false,
        }}
      >
        Annuler et quitter
      </ButtonLink>
      <SubmitButton isLoading={isSubmitting}>
        Enregistrer et quitter
      </SubmitButton>
    </div>
  )
}
