import { createPortal } from 'react-dom'

import { orejimeRef } from '@/app/App/analytics/orejime'
import { useSkipLinksContext } from '@/components/SkipLinks/SkipLinksContext'
import { Button } from '@/design-system/Button/Button'
import {
  ButtonColor,
  ButtonSize,
  ButtonVariant,
} from '@/design-system/Button/types'
import fullNextIcon from '@/icons/full-next.svg'

import styles from './Footer.module.scss'

type FooterProps = {
  isUnauthenticated?: boolean
}

export const Footer = ({
  isUnauthenticated = false,
}: Readonly<FooterProps>): JSX.Element => {
  const { footerContainer } = useSkipLinksContext()

  const isAuthenticated = isUnauthenticated === false

  return (
    // biome-ignore lint/correctness/useUniqueElementIds: Footer is used once per page. There cannot be id duplications.
    <footer
      className={styles['footer']}
      data-testid="app-footer"
      id="pied-de-page"
      tabIndex={-1}
    >
      {footerContainer &&
        createPortal(
          <Button
            as="a"
            to="#pied-de-page"
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
            opensInNewTab
            label="Charte des Données Personnelles"
          />
        </li>
        <li className={styles['footer-list-item']}>
          <Button
            as="router-link"
            variant={ButtonVariant.TERTIARY}
            color={ButtonColor.NEUTRAL}
            size={ButtonSize.SMALL}
            to="/accessibilite"
            label="Accessibilité : partiellement conforme"
          />
        </li>
        <li className={styles['footer-list-item']}>
          <Button
            as="router-link"
            variant={ButtonVariant.TERTIARY}
            color={ButtonColor.NEUTRAL}
            size={ButtonSize.SMALL}
            to="/ecoconception"
            label="Déclaration d’écoconception"
          />
        </li>
        {isAuthenticated && (
          <li className={styles['footer-list-item']}>
            <Button
              as="router-link"
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
            onClick={() => orejimeRef.current?.prompt()}
            label="Gestion des cookies"
          />
        </li>
      </ul>
    </footer>
  )
}
