import cn from 'classnames'
import React from 'react'

import { orejime } from 'app/App/analytics/orejime'
import { useIsNewInterfaceActive } from 'hooks/useIsNewInterfaceActive'
import { Button } from 'ui-kit/Button/Button'
import { ButtonLink } from 'ui-kit/Button/ButtonLink'
import { ButtonVariant } from 'ui-kit/Button/types'

import styles from './CookiesFooter.module.scss'

export const CookiesFooter = ({ className }: { className?: string }) => {
  const isNewSideBarNavigation = useIsNewInterfaceActive()

  if (isNewSideBarNavigation) {
    return
  }

  return (
    <footer>
      <nav>
        <ul className={cn(styles['cookies-footer'], className)}>
          <li>
            <ButtonLink
              variant={ButtonVariant.QUATERNARY}
              link={{
                to: 'https://pass.culture.fr/cgu-professionnels/',
                isExternal: true,
                target: '_blank',
              }}
            >
              CGU professionnels
            </ButtonLink>
          </li>
          <li>
            <ButtonLink
              variant={ButtonVariant.QUATERNARY}
              link={{
                to: '/accessibilite',
              }}
            >
              Accessibilité : non conforme
            </ButtonLink>
          </li>
          <li>
            <ButtonLink
              variant={ButtonVariant.QUATERNARY}
              link={{
                to: 'https://pass.culture.fr/donnees-personnelles/',
                isExternal: true,
                target: '_blank',
              }}
            >
              Charte des Données Personnelles
            </ButtonLink>
          </li>
          <li>
            <Button
              variant={ButtonVariant.QUATERNARY}
              onClick={() => orejime.show()}
            >
              Gestion des cookies
            </Button>
          </li>
        </ul>
      </nav>
    </footer>
  )
}
