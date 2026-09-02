import { Button } from '@/design-system/Button/Button'
import { ButtonColor, ButtonVariant } from '@/design-system/Button/types'

import styles from './VenueManagement.module.scss'

const VenueManagement = () => {
  return (
    <div className={styles.banner}>
      <div className={styles.container}>
        <h2 className={styles.title}>Fermeture de la structure</h2>
        <p className={styles.description}>
          Toutes vos offres seront retirées du pass Culture.
        </p>
      </div>
      <Button
        variant={ButtonVariant.PRIMARY}
        color={ButtonColor.DANGER}
        label="Fermer la structure"
      />
    </div>
  )
}

// Lazy-loaded by react-router
// ts-unused-exports:disable-next-line
export const Component = VenueManagement
