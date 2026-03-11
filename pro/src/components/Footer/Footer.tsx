import classNames from 'classnames'
import { createPortal } from 'react-dom'

import { orejime } from '@/app/App/analytics/orejime'
import { useAppSelector } from '@/commons/hooks/useAppSelector'
import { selectCurrentUser } from '@/commons/store/user/selectors'
import { Button } from '@/design-system/Button/Button'
import {
  ButtonColor,
  ButtonSize,
  ButtonVariant,
} from '@/design-system/Button/types'
import fullNextIcon from '@/icons/full-next.svg'

import { useSkipLinksContext } from '../SkipLinks/SkipLinksContext'
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
  const { footerContainer } = useSkipLinksContext()

  return (
    // biome-ignore lint/correctness/useUniqueElementIds: Footer is used once per page. There cannot be id duplications.
    <footer
      className={classNames(
        styles['footer'],
        styles[`footer-layout-${layout}`]
      )}
      data-testid="app-footer"
      id="pied-de-page"
      tabIndex={-1}
    >
      {footerContainer &&
        createPortal(
          // biome-ignore lint/correctness/useUniqueElementIds: Go to footer link is used once per page. There cannot be id duplications.
          <Button
            as="a"
            to="#pied-de-page"
            isExternal
            icon={fullNextIcon}
            label="Aller au pied de page"
            size={ButtonSize.SMALL}
            variant={ButtonVariant.SECONDARY}
            color={ButtonColor.NEUTRAL}
          />,
          footerContainer
        )}
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
