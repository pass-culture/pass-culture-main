import { GetVenueResponseModel } from '@/apiClient//v1'
import { getVenuePagePathToNavigateTo } from '@/commons/utils/getVenuePagePathToNavigateTo'
import { Button } from '@/ui-kit/Button/Button'
import { ButtonLink } from '@/ui-kit/Button/ButtonLink'
import { ButtonVariant } from '@/ui-kit/Button/types'

import styles from './VenueFormActionBar.module.scss'

export interface VenueFormActionBarProps {
  venue?: GetVenueResponseModel
  isSubmitting?: boolean
  disableFormSubmission?: boolean
}

export const VenueFormActionBar = ({
  venue,
  disableFormSubmission,
  isSubmitting = false,
}: VenueFormActionBarProps) => {
  return (
    <div className={styles['action-bar']}>
      <ButtonLink
        variant={ButtonVariant.SECONDARY}
        to={getVenuePagePathToNavigateTo(
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
