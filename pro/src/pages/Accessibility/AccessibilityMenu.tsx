import { useNavigate } from 'react-router'

import { FullLayout } from '@/app/App/layouts/FullLayout/FullLayout'
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

import styles from './AccessibilityMenu.module.scss'

export function AccessibilityMenu() {
  const user = useAppSelector(selectCurrentUser)
  const isUserConnected = !!user
  const navigate = useNavigate()

  const backToDefault = () => {
    isUserConnected ? void navigate('/accueil') : void navigate('/connexion')
  }

  return (
    <FullLayout>
      <div className={styles['content-wrapper']}>
        <h1 className={styles['title']}>Informations d'accessibilité</h1>
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
              as="router-link"
              to="/accessibilite/engagements"
              variant={ButtonVariant.SECONDARY}
              color={ButtonColor.NEUTRAL}
              icon={strokeRigthIcon}
              iconPosition={IconPositionEnum.RIGHT}
              label="Les engagements du pass Culture"
            />
            <Button
              as="router-link"
              to="/accessibilite/declaration"
              variant={ButtonVariant.SECONDARY}
              color={ButtonColor.NEUTRAL}
              icon={strokeRigthIcon}
              iconPosition={IconPositionEnum.RIGHT}
              label="Déclaration d'accessibilité"
            />
            <Button
              as="a"
              to="https://pass.culture.fr/schema-pluriannuel-2025-2027"
              opensInNewTab
              variant={ButtonVariant.SECONDARY}
              color={ButtonColor.NEUTRAL}
              icon={strokeRigthIcon}
              iconPosition={IconPositionEnum.RIGHT}
              label="Schéma pluriannuel"
            />
          </div>
        </div>
      </div>
    </FullLayout>
  )
}

// Lazy-loaded by react-router
// ts-unused-exports:disable-next-line
export const Component = AccessibilityMenu
