import { Button } from '@/design-system/Button/Button'
import { ButtonColor, ButtonVariant } from '@/design-system/Button/types'

import styles from './VenueFormActionBar.module.scss'

export interface VenueFormActionBarProps {
  isSubmitting?: boolean
}

export const VenueFormActionBar = ({
  isSubmitting = false,
}: VenueFormActionBarProps) => {
  return (
    <div className={styles['action-bar']}>
      <Button
        as="a"
        variant={ButtonVariant.SECONDARY}
        color={ButtonColor.NEUTRAL}
        to="/parametres"
        label="Annuler"
        fullWidth
      />
      <Button
        type="submit"
        isLoading={isSubmitting}
        label="Enregistrer"
        fullWidth
      />
    </div>
  )
}
