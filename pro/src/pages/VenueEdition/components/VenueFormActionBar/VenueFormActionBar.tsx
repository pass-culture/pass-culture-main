import { Button } from '@/design-system/Button/Button'
import { ButtonColor, ButtonVariant } from '@/design-system/Button/types'

import styles from './VenueFormActionBar.module.scss'

export interface VenueFormActionBarProps {
  isSubmitting?: boolean
  disableFormSubmission?: boolean
  isSettingsPage?: boolean
}

export const VenueFormActionBar = ({
  disableFormSubmission,
  isSubmitting = false,
  isSettingsPage = false,
}: VenueFormActionBarProps) => {
  return (
    <div className={styles['action-bar']}>
      <Button
        as="a"
        variant={ButtonVariant.SECONDARY}
        color={ButtonColor.NEUTRAL}
        to={isSettingsPage ? '/parametres' : '/partenaire/page-partenaire'}
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
