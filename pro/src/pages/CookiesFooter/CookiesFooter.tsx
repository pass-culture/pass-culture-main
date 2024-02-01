import cn from 'classnames'
import React from 'react'

import { Button } from 'ui-kit'
import ButtonLink from 'ui-kit/Button/ButtonLink'
import { ButtonVariant } from 'ui-kit/Button/types'
import { initCookieConsent } from 'utils/cookieConsentModal'

import styles from './CookiesFooter.module.scss'

const CookiesFooter = ({ className }: { className?: string }): JSX.Element => (
  <footer>
    <nav>
      <ul className={cn(styles['cookies-footer'], className)}>
        <li>
          <ButtonLink
            variant={ButtonVariant.QUATERNARY}
            className={styles['cookies-footer-link']}
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
            className={styles['cookies-footer-link']}
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
            className={styles['cookies-footer-link']}
            onClick={() => initCookieConsent().show()}
          >
            Gestion des cookies
          </Button>
        </li>
      </ul>
    </nav>
  </footer>
)

export default CookiesFooter
