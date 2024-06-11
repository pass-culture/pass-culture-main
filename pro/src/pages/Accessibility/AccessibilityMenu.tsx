import strokeRigthIcon from 'icons/stroke-right.svg'
import { ButtonLink } from 'ui-kit/Button/ButtonLink'
import { ButtonVariant, IconPositionEnum } from 'ui-kit/Button/types'

import { AccessibilityLayout } from './AccessibilityLayout'
import styles from './AccessibilityMenu.module.scss'

export function AccessibilityMenu() {
  return (
    <AccessibilityLayout showBackToSignInButton>
      <h1 className={styles['title-accessibility']}>
        Informations d’accessibilité
      </h1>

      <div className={styles['menu-accessibility']}>
        <ButtonLink
          link={{
            to: `/accessibilite/engagements`,
          }}
          variant={ButtonVariant.BOX}
          icon={strokeRigthIcon}
          iconPosition={IconPositionEnum.RIGHT}
          className={styles['button-link']}
        >
          Les engagements du pass Culture
        </ButtonLink>
        <ButtonLink
          link={{
            to: `/accessibilite/declaration`,
          }}
          variant={ButtonVariant.BOX}
          icon={strokeRigthIcon}
          className={styles['button-link']}
          iconPosition={IconPositionEnum.RIGHT}
        >
          Déclaration d’accessibilité
        </ButtonLink>
        <ButtonLink
          link={{
            to: `/accessibilite/schema-pluriannuel`,
          }}
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

// Lazy-loaded by react-router-dom
// ts-unused-exports:disable-next-line
export const Component = AccessibilityMenu
