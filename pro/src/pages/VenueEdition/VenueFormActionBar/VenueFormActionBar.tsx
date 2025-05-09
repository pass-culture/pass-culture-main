import { useFormContext } from 'react-hook-form'

import { GetVenueResponseModel } from 'apiClient/v1'
import { VenueSettingsFormValues } from 'pages/VenueSettings/types'
import { Button } from 'ui-kit/Button/Button'
import { ButtonLink } from 'ui-kit/Button/ButtonLink'
import { ButtonVariant } from 'ui-kit/Button/types'

import { getPathToNavigateTo } from '../context'
import { VenueEditionFormValues } from '../types'

import styles from './VenueFormActionBar.module.scss'

export interface VenueFormActionBarProps {
  venue?: GetVenueResponseModel
  disableFormSubmission?: boolean
}

export const VenueFormActionBar = ({
  venue,
  disableFormSubmission,
}: VenueFormActionBarProps) => {
  const {
    formState: { isSubmitting },
  } = useFormContext<VenueEditionFormValues | VenueSettingsFormValues>()

  return (
    <div className={styles['action-bar']}>
      <ButtonLink
        variant={ButtonVariant.SECONDARY}
        to={getPathToNavigateTo(
          venue?.managingOfferer.id as number,
          venue?.id as number
        )}
      >
        Annuler
      </ButtonLink>
      <Button
        type="submit"
        isLoading={isSubmitting}
        disabled={disableFormSubmission}
      >
        Enregistrer
      </Button>
    </div>
  )
}
