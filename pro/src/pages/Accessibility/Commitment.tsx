import fullBackIcon from 'icons/full-back.svg'
import { ButtonLink } from 'ui-kit/Button/ButtonLink'

import { AccessibilityLayout } from './AccessibilityLayout'
import styles from './Commitment.module.scss'

export const Commitment = () => {
  return (
    <AccessibilityLayout>
      <ButtonLink
        link={{
          to: '/accessibilite/',
        }}
        icon={fullBackIcon}
      >
        Retour vers la page Informations d’accessibilité
      </ButtonLink>
      <h1 className={styles['title-accessibility']}>
        Les engagements du pass Culture
      </h1>
    </AccessibilityLayout>
  )
}
// Lazy-loaded by react-router-dom
// ts-unused-exports:disable-next-line
export const Component = Commitment
