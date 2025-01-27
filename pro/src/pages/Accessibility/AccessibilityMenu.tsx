import strokeRigthIcon from 'icons/stroke-right.svg'
import { ButtonLink } from 'ui-kit/Button/ButtonLink'
import { ButtonVariant, IconPositionEnum } from 'ui-kit/Button/types'

import { AccessibilityLayout } from './AccessibilityLayout'
import styles from './AccessibilityMenu.module.scss'

export function AccessibilityMenu() {
  return (
    <AccessibilityLayout
      mainHeading="Informations d’accessibilité"
      showBackToSignInButton
    >
      <div className={styles['menu-accessibility']}>
        <ButtonLink
          to="/accessibilite/engagements"
          variant={ButtonVariant.BOX}
          icon={strokeRigthIcon}
          iconPosition={IconPositionEnum.RIGHT}
          className={styles['button-link']}
        >
          Les engagements du pass Culture
        </ButtonLink>
        <ButtonLink
          to="/accessibilite/declaration"
          variant={ButtonVariant.BOX}
          icon={strokeRigthIcon}
          className={styles['button-link']}
          iconPosition={IconPositionEnum.RIGHT}
        >
          Déclaration d’accessibilité
        </ButtonLink>
        <ButtonLink
          to="/accessibilite/schema-pluriannuel"
          variant={ButtonVariant.BOX}
          icon={strokeRigthIcon}
          className={styles['button-link']}
          iconPosition={IconPositionEnum.RIGHT}
        >
          Schéma pluriannuel
        </ButtonLink>
      </div>
    </AccessibilityLayout>
  )
}

// Lazy-loaded by react-router
// ts-unused-exports:disable-next-line
export const Component = AccessibilityMenu
