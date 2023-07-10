import cn from 'classnames'
import React from 'react'

import useActiveFeature from 'hooks/useActiveFeature'
import { Button } from 'ui-kit'
import ButtonLink from 'ui-kit/Button/ButtonLink'
import { ButtonVariant } from 'ui-kit/Button/types'
import { initCookieConsent } from 'utils/cookieConsentModal'

import styles from './CookiesFooter.module.scss'

const CookiesFooter = ({ className }: { className?: string }): JSX.Element => {
  const isCookieBannerEnabled = useActiveFeature('WIP_ENABLE_COOKIES_BANNER')
  if (!isCookieBannerEnabled) {
    return <></>
  }

  return (
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
                rel: 'noopener noreferrer',
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
                rel: 'noopener noreferrer',
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
}

export default CookiesFooter
