import { Button } from '@/design-system/Button/Button'
import { ButtonColor, ButtonVariant } from '@/design-system/Button/types'
import iconFullNext from '@/icons/full-next.svg'

import styles from './AlreadyHasAccount.module.scss'

export const AlreadyHasAccount = (): JSX.Element => {
  return (
    <div className={styles['existing-account']}>
      <p className={styles['existing-account-text']}>
        Vous avez déjà un compte ?
      </p>

      <Button
        as="a"
        to="/connexion"
        icon={iconFullNext}
        variant={ButtonVariant.TERTIARY}
        color={ButtonColor.NEUTRAL}
        label="Se connecter"
      />
    </div>
  )
}
