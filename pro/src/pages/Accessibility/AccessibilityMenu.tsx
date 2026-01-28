import { Button } from '@/design-system/Button/Button'
import {
  ButtonColor,
  ButtonVariant,
  IconPositionEnum,
} from '@/design-system/Button/types'
import strokeRigthIcon from '@/icons/stroke-right.svg'

import { AccessibilityLayout } from './AccessibilityLayout'
import styles from './AccessibilityMenu.module.scss'

export function AccessibilityMenu() {
  return (
    <AccessibilityLayout
      mainHeading="Informations d’accessibilité"
      showBackToSignInButton
    >
      <div className={styles['menu-accessibility']}>
        <Button
          as="a"
          to="/accessibilite/engagements"
          variant={ButtonVariant.SECONDARY}
          color={ButtonColor.NEUTRAL}
          icon={strokeRigthIcon}
          iconPosition={IconPositionEnum.RIGHT}
          label="Les engagements du pass Culture"
        />
        <Button
          as="a"
          to="/accessibilite/declaration"
          variant={ButtonVariant.SECONDARY}
          color={ButtonColor.NEUTRAL}
          icon={strokeRigthIcon}
          iconPosition={IconPositionEnum.RIGHT}
          label="Déclaration d’accessibilité"
        />
        <Button
          as="a"
          to="/accessibilite/schema-pluriannuel"
          variant={ButtonVariant.SECONDARY}
          color={ButtonColor.NEUTRAL}
          icon={strokeRigthIcon}
          iconPosition={IconPositionEnum.RIGHT}
          label="Schéma pluriannuel"
        />
      </div>
    </AccessibilityLayout>
  )
}

// Lazy-loaded by react-router
// ts-unused-exports:disable-next-line
export const Component = AccessibilityMenu
