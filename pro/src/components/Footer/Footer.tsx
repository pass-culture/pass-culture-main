import classNames from 'classnames'

import useActiveFeature from 'hooks/useActiveFeature'
import useCurrentUser from 'hooks/useCurrentUser'
import { Button, ButtonLink } from 'ui-kit'
import { ButtonVariant } from 'ui-kit/Button/types'
import { initCookieConsent } from 'utils/cookieConsentModal'

import styles from './Footer.module.scss'

type FooterProps = {
  layout?: 'basic' | 'funnel' | 'without-nav' | 'sticky-actions'
}
export default function Footer({ layout }: FooterProps) {
  const isNewSideBarNavigation = useActiveFeature('WIP_ENABLE_PRO_SIDE_NAV')

  const { currentUser } = useCurrentUser()
  if (!isNewSideBarNavigation) {
    return
  }

  return (
    <footer
      className={classNames(
        styles['footer'],
        styles[`footer-layout-${layout}`]
      )}
    >
      <ul>
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
        {currentUser && (
          <li>
            <ButtonLink
              variant={ButtonVariant.QUATERNARY}
              className={styles['cookies-footer-link']}
              link={{
                to: '/plan-du-site',
              }}
            >
              Plan du site
            </ButtonLink>
          </li>
        )}
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
    </footer>
  )
}
