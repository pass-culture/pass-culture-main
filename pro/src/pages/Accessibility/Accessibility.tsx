import { AppLayout } from 'app/AppLayout'
import strokeRigthIcon from 'icons/stroke-right.svg'
import { ButtonLink } from 'ui-kit/Button/ButtonLink'
import { ButtonVariant, IconPositionEnum } from 'ui-kit/Button/types'

import styles from './Accessibility.module.scss'

export const Accessibility = () => {
  return (
    <AppLayout>
      <h1 className={styles['title-accessibility']}>
        Informations d’accessibilité
      </h1>

      <div className={styles['menu-accessibility']}>
        <ButtonLink
          link={{
            to: `accessibilite/engagements`,
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
            to: `accessibilite/schema-pluriannuel`,
          }}
          variant={ButtonVariant.BOX}
          icon={strokeRigthIcon}
          className={styles['button-link']}
          iconPosition={IconPositionEnum.RIGHT}
        >
          Schéma pluriannuel
        </ButtonLink>
      </div>
    </AppLayout>
  )
}
// Lazy-loaded by react-router-dom
// ts-unused-exports:disable-next-line
export const Component = Accessibility
