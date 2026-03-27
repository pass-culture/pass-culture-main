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

import { EcoDesignLayout } from './EcoDesignLayout'
import styles from './EcoDesignMenu.module.scss'

export const EcoDesignMenu = () => {
  const user = useAppSelector(selectCurrentUser)
  const isUserConnected = !!user
  const navigate = useNavigate()

  const backToDefault = () => {
    isUserConnected ? navigate('/accueil') : navigate('/connexion')
  }

  return (
    <EcoDesignLayout mainHeading="Déclaration d'écoconception de l'espace partenaires">
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
            to="/ecoconception/politique"
            variant={ButtonVariant.SECONDARY}
            color={ButtonColor.NEUTRAL}
            icon={strokeRigthIcon}
            iconPosition={IconPositionEnum.RIGHT}
            label="Politique d'écoconception au pass Culture"
          />
          <Button
            as="a"
            to="/ecoconception/declaration"
            variant={ButtonVariant.SECONDARY}
            color={ButtonColor.NEUTRAL}
            icon={strokeRigthIcon}
            iconPosition={IconPositionEnum.RIGHT}
            label="Déclaration RGESN"
          />
        </div>
      </div>
    </EcoDesignLayout>
  )
}

// Lazy-loaded by react-router
// ts-unused-exports:disable-next-line
export const Component = EcoDesignMenu
