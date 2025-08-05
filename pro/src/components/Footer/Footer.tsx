import { orejime } from 'app/App/analytics/orejime'
import classNames from 'classnames'
import { selectCurrentUser } from 'commons/store/user/selectors'
import fullLinkIcon from 'icons/full-link.svg'
import { useSelector } from 'react-redux'
import { Button } from 'ui-kit/Button/Button'
import { ButtonLink } from 'ui-kit/Button/ButtonLink'
import { ButtonVariant } from 'ui-kit/Button/types'

import styles from './Footer.module.scss'

type FooterProps = {
  layout?:
    | 'basic'
    | 'funnel'
    | 'onboarding'
    | 'sticky-actions'
    | 'sticky-onboarding'
    | 'logged-out'
    | 'sign-up'
}
export const Footer = ({ layout }: FooterProps) => {
  const currentUser = useSelector(selectCurrentUser)

  return (
    <footer
      className={classNames(
        styles['footer'],
        styles[`footer-layout-${layout}`]
      )}
      data-testid="app-footer"
    >
      <ul className={styles['footer-list']}>
        <li className={styles['footer-list-item']}>
          <ButtonLink
            variant={ButtonVariant.QUATERNARY}
            to="https://pass.culture.fr/cgu-professionnels/"
            isExternal
            opensInNewTab
            icon={fullLinkIcon}
          >
            CGU professionnels
          </ButtonLink>
        </li>
        <li className={styles['footer-list-item']}>
          <ButtonLink
            variant={ButtonVariant.QUATERNARY}
            to="https://pass.culture.fr/donnees-personnelles/"
            isExternal
            opensInNewTab
            icon={fullLinkIcon}
          >
            Charte des Données Personnelles
          </ButtonLink>
        </li>
        <li className={styles['footer-list-item']}>
          <ButtonLink variant={ButtonVariant.QUATERNARY} to="/accessibilite">
            Accessibilité : non conforme
          </ButtonLink>
        </li>
        {currentUser && (
          <li className={styles['footer-list-item']}>
            <ButtonLink variant={ButtonVariant.QUATERNARY} to="/plan-du-site">
              Plan du site
            </ButtonLink>
          </li>
        )}
        <li className={styles['footer-list-item']}>
          <Button
            variant={ButtonVariant.QUATERNARY}
            onClick={() => orejime.prompt()}
          >
            Gestion des cookies
          </Button>
        </li>
      </ul>
    </footer>
  )
}
