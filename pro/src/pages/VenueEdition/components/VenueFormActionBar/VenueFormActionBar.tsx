import { Button } from '@/design-system/Button/Button'
import { ButtonColor, ButtonVariant } from '@/design-system/Button/types'

import styles from './VenueFormActionBar.module.scss'

export interface VenueFormActionBarProps {
  isSubmitting?: boolean
  disableFormSubmission?: boolean
  onCancel?: () => void
}

export const VenueFormActionBar = ({
  disableFormSubmission,
  isSubmitting = false,
  onCancel,
}: VenueFormActionBarProps) => {
  return (
    <div className={styles['action-bar']}>
      <Button
        variant={ButtonVariant.SECONDARY}
        color={ButtonColor.NEUTRAL}
        onClick={onCancel}
        label="Annuler"
        fullWidth
      />
      <Button
        type="submit"
        isLoading={isSubmitting}
        disabled={disableFormSubmission}
        label="Enregistrer"
        fullWidth
      />
    </div>
  )
}
