import { Button } from '@/design-system/Button/Button'
import { ButtonVariant } from '@/design-system/Button/types'
import commonStyles from '@/pages/Simulator/CommonSimulator.module.scss'

import styles from './SimulatorEmailConfirmation.module.scss'

export const SimulatorEmailConfirmation = (): JSX.Element => {
  return (
    <div className={commonStyles['content']}>
      <h1 className={styles['title']}>C'est envoyé !</h1>
      <p className={commonStyles['subtitle']}>
        Votre liste personnalisée a bien été envoyée. Préparez sereinement vos
        justificatifs et reprenez votre inscription quand vous le souhaitez, en
        cliquant sur le lien inclus dans l’email.
      </p>
      <Button
        as="a"
        to="/inscription/preparation/resultats"
        label="Retour à l'inscription"
        variant={ButtonVariant.SECONDARY}
      />
    </div>
  )
}

// Lazy-loaded by react-router
// ts-unused-exports:disable-next-line
export const Component = SimulatorEmailConfirmation
