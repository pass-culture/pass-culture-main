import classNames from 'classnames'

import { orejime } from '@/app/App/analytics/orejime'
import { useAppSelector } from '@/commons/hooks/useAppSelector'
import { selectCurrentUser } from '@/commons/store/user/selectors'
import { Button } from '@/design-system/Button/Button'
import {
  ButtonColor,
  ButtonSize,
  ButtonVariant,
} from '@/design-system/Button/types'
import fullLinkIcon from '@/icons/full-link.svg'

import styles from './Footer.module.scss'

type FooterProps = {
  layout?:
    | 'basic'
    | 'sticky-basic'
    | 'onboarding'
    | 'sticky-onboarding'
    | 'logged-out'
    | 'sign-up'
}
export const Footer = ({ layout }: FooterProps) => {
  const currentUser = useAppSelector(selectCurrentUser)

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
          <Button
            as="a"
            variant={ButtonVariant.TERTIARY}
            color={ButtonColor.NEUTRAL}
            size={ButtonSize.SMALL}
            to="https://pass.culture.fr/cgu-professionnels/"
            isExternal
            opensInNewTab
            icon={fullLinkIcon}
            label="CGU professionnels"
          />
        </li>
        <li className={styles['footer-list-item']}>
          <Button
            as="a"
            variant={ButtonVariant.TERTIARY}
            color={ButtonColor.NEUTRAL}
            size={ButtonSize.SMALL}
            to="https://pass.culture.fr/donnees-personnelles/"
            isExternal
            opensInNewTab
            icon={fullLinkIcon}
            label="Charte des Données Personnelles"
          />
        </li>
        <li className={styles['footer-list-item']}>
          <Button
            as="a"
            variant={ButtonVariant.TERTIARY}
            color={ButtonColor.NEUTRAL}
            size={ButtonSize.SMALL}
            to="/accessibilite"
            label="Accessibilité : non conforme"
          />
        </li>
        {currentUser && (
          <li className={styles['footer-list-item']}>
            <Button
              as="a"
              variant={ButtonVariant.TERTIARY}
              color={ButtonColor.NEUTRAL}
              size={ButtonSize.SMALL}
              to="/plan-du-site"
              label="Plan du site"
            />
          </li>
        )}
        <li className={styles['footer-list-item']}>
          <Button
            variant={ButtonVariant.TERTIARY}
            color={ButtonColor.NEUTRAL}
            size={ButtonSize.SMALL}
            onClick={() => orejime?.prompt()}
            label="Gestion des cookies"
          />
        </li>
      </ul>
    </footer>
  )
}
