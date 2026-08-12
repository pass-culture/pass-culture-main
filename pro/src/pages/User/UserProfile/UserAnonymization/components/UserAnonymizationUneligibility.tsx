import { Button } from '@/design-system/Button/Button'
import { ButtonColor, ButtonVariant } from '@/design-system/Button/types'

import styles from './UserAnonymizationUneligibility.module.scss'

const PERSONAL_DATA_CHARTER_URL =
  'https://pass.culture.fr/donnees-personnelles/'

interface UserAnonymizationUneligibilityProps {
  isSoleUserWithOngoingActivities?: boolean
  onClose: () => void
}

export const UserAnonymizationUneligibility = ({
  isSoleUserWithOngoingActivities,
  onClose,
}: UserAnonymizationUneligibilityProps): JSX.Element => {
  return (
    <>
      <div className={styles['dialog-content']}>
        <p className={styles['description']}>
          {isSoleUserWithOngoingActivities
            ? 'Des offres ou réservations sont toujours en cours dans votre structure. '
            : ''}
          Pour plus d’informations, consultez notre charte des données
          personnelles :
        </p>
        <Button
          as="a"
          to={PERSONAL_DATA_CHARTER_URL}
          opensInNewTab
          variant={ButtonVariant.TERTIARY}
          color={ButtonColor.NEUTRAL}
          label="Lire la charte des données personnelles"
        />
      </div>
      <div className={styles['dialog-footer']}>
        <Button onClick={onClose} label="J'ai compris" />
      </div>
    </>
  )
}
