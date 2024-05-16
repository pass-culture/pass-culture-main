import classNames from 'classnames'
import { useSelector } from 'react-redux'

import { orejime } from 'app/App/analytics/orejime'
import useIsNewInterfaceActive from 'hooks/useIsNewInterfaceActive'
import fullLinkIcon from 'icons/full-link.svg'
import { selectCurrentUser } from 'store/user/selectors'
import { Button } from 'ui-kit/Button/Button'
import { ButtonLink } from 'ui-kit/Button/ButtonLink'
import { ButtonVariant } from 'ui-kit/Button/types'

import styles from './Footer.module.scss'

type FooterProps = {
  layout?: 'basic' | 'funnel' | 'without-nav' | 'sticky-actions'
}
export default function Footer({ layout }: FooterProps) {
  const currentUser = useSelector(selectCurrentUser)
  const isNewSideBarNavigation = useIsNewInterfaceActive()

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
            icon={fullLinkIcon}
            svgAlt="Nouvelle fenêtre"
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
            icon={fullLinkIcon}
            svgAlt="Nouvelle fenêtre"
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
            onClick={() => orejime.show()}
          >
            Gestion des cookies
          </Button>
        </li>
      </ul>
    </footer>
  )
}
