import { useNavigate } from 'react-router'

import { useAppSelector } from '@/commons/hooks/useAppSelector'
import { selectCurrentUser } from '@/commons/store/user/selectors'
import { Button } from '@/design-system/Button/Button'
import {
  ButtonColor,
  ButtonVariant,
  IconPositionEnum,
} from '@/design-system/Button/types'
import fullBackIcon from '@/icons/full-back.svg'
import strokeRigthIcon from '@/icons/stroke-right.svg'

import { AccessibilityLayout } from './AccessibilityLayout'
import styles from './AccessibilityMenu.module.scss'

export function AccessibilityMenu() {
  const user = useAppSelector(selectCurrentUser)
  const isUserConnected = !!user
  const navigate = useNavigate()

  const backToDefault = () => {
    isUserConnected ? navigate('/accueil') : navigate('/connexion')
  }

  return (
    <AccessibilityLayout
      mainHeading="Informations d’accessibilité"
      showBackToSignInButton
    >
      <div className={styles['page-content']}>
        <Button
          onClick={() => backToDefault()}
          variant={ButtonVariant.TERTIARY}
          color={ButtonColor.NEUTRAL}
          icon={fullBackIcon}
          iconPosition={IconPositionEnum.LEFT}
          label="Retour"
        />
        <div className={styles['pages-buttons-container']}>
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
      </div>
    </AccessibilityLayout>
  )
}

// Lazy-loaded by react-router
// ts-unused-exports:disable-next-line
export const Component = AccessibilityMenu
