import * as Dialog from '@radix-ui/react-dialog'

import { Button } from '@/ui-kit/Button/Button'
import { ButtonLink } from '@/ui-kit/Button/ButtonLink'
import { ButtonVariant } from '@/ui-kit/Button/types'

import styles from './UserAnonymizationUneligibility.module.scss'

const PERSONAL_DATA_CHARTER_URL =
  'https://pass.culture.fr/donnees-personnelles/'

interface UserAnonymizationUneligibilityProps {
  isSoleUserWithOngoingActivities?: boolean
}

export const UserAnonymizationUneligibility = ({
  isSoleUserWithOngoingActivities,
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
        <ButtonLink
          to={PERSONAL_DATA_CHARTER_URL}
          isExternal
          opensInNewTab
          variant={ButtonVariant.TERNARY}
        >
          Lire la charte des données personnelles
        </ButtonLink>
      </div>
      <div className={styles['dialog-footer']}>
        <Dialog.Close asChild>
          <Button variant={ButtonVariant.PRIMARY}>J‘ai compris</Button>
        </Dialog.Close>
      </div>
    </>
  )
}
