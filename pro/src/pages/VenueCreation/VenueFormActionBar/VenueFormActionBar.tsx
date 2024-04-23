import { useFormikContext } from 'formik'
import React from 'react'

import { GetVenueResponseModel } from 'apiClient/v1'
import { Button } from 'ui-kit/Button/Button'
import { ButtonLink } from 'ui-kit/Button/ButtonLink'
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
      <Button type="submit" isLoading={isSubmitting}>
        Enregistrer et quitter
      </Button>
    </div>
  )
}
