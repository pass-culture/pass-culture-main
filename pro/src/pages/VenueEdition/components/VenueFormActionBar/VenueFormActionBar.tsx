import { getVenuePagePathToNavigateTo } from '@/commons/utils/getVenuePagePathToNavigateTo'
import { Button } from '@/design-system/Button/Button'
import { ButtonColor, ButtonVariant } from '@/design-system/Button/types'

import styles from './VenueFormActionBar.module.scss'

export interface VenueFormActionBarProps {
  isSubmitting?: boolean
  disableFormSubmission?: boolean
}

export const VenueFormActionBar = ({
  disableFormSubmission,
  isSubmitting = false,
}: VenueFormActionBarProps) => {
  return (
    <div className={styles['action-bar']}>
      <Button
        as="a"
        variant={ButtonVariant.SECONDARY}
        color={ButtonColor.NEUTRAL}
        to={getVenuePagePathToNavigateTo()}
        label="Annuler"
      />
      <Button
        type="submit"
        isLoading={isSubmitting}
        disabled={disableFormSubmission}
        label="Enregistrer"
      />
    </div>
  )
}
