import cn from 'classnames'
import React from 'react'

import { orejime } from 'app/App/analytics/orejime'
import { Button } from 'ui-kit/Button/Button'
import { ButtonLink } from 'ui-kit/Button/ButtonLink'
import { ButtonVariant } from 'ui-kit/Button/types'

import styles from './CookiesFooter.module.scss'

export const CookiesFooter = ({ className }: { className?: string }) => {
  return (
    <footer>
      <nav>
        <ul className={cn(styles['cookies-footer'], className)}>
          <li>
            <ButtonLink
              variant={ButtonVariant.QUATERNARY}
              to="https://pass.culture.fr/cgu-professionnels/"
              isExternal
              opensInNewTab
            >
              CGU professionnels
            </ButtonLink>
          </li>
          <li>
            <ButtonLink variant={ButtonVariant.QUATERNARY} to="/accessibilite">
              Accessibilité : non conforme
            </ButtonLink>
          </li>
          <li>
            <ButtonLink
              variant={ButtonVariant.QUATERNARY}
              className={styles['cookies-footer-link']}
              to="https://pass.culture.fr/donnees-personnelles/"
              isExternal
              opensInNewTab
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
