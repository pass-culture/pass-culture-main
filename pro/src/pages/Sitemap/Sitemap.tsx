import { Link, useNavigate } from 'react-router'

import { BasicLayout } from '@/app/App/layouts/BasicLayout/BasicLayout'
import { useAppSelector } from '@/commons/hooks/useAppSelector'
import { selectCurrentOffererId } from '@/commons/store/offerer/selectors'
import { Button } from '@/design-system/Button/Button'
import {
  ButtonColor,
  ButtonVariant,
  IconPositionEnum,
} from '@/design-system/Button/types'
import fullBackIcon from '@/icons/full-back.svg'

import styles from './Sitemap.module.scss'

export const Sitemap = () => {
  const selectedOffererId = useAppSelector(selectCurrentOffererId)
  const navigate = useNavigate()

  return (
    <BasicLayout mainHeading="Plan du site" displayLateralPanel={false}>
      <Button
        onClick={() => navigate(-1)}
        color={ButtonColor.NEUTRAL}
        variant={ButtonVariant.TERTIARY}
        icon={fullBackIcon}
        iconPosition={IconPositionEnum.LEFT}
        label="Retour"
      />
      <ul className={styles['sitemap-list']} data-testid="sitemap">
        <li className={styles['sitemap-list-item']}>
          <Link
            to={`/offre/creation?structure=${selectedOffererId}`}
            className={styles['sitemap-link']}
          >
            Créer une offre
          </Link>
        </li>
        <li className={styles['sitemap-list-item']}>
          <Link to="/accueil" className={styles['sitemap-link']}>
            Accueil
          </Link>
        </li>
        <li className={styles['sitemap-list-item']}>
          <span className={styles['sitemap-list-title']}>Individuel</span>
          <ul className={styles['sitemap-sub-list']}>
            <li className={styles['sitemap-list-item']}>
              <Link to="/offres" className={styles['sitemap-link']}>
                Offres
              </Link>
            </li>
            <li className={styles['sitemap-list-item']}>
              <Link to="/reservations" className={styles['sitemap-link']}>
                Réservations
              </Link>
            </li>
            <li className={styles['sitemap-list-item']}>
              <Link to="/guichet" className={styles['sitemap-link']}>
                Guichet
              </Link>
            </li>
          </ul>
        </li>

        <li className={styles['sitemap-list-item']}>
          <span className={styles['sitemap-list-title']}>Collectif</span>
          <ul className={styles['sitemap-sub-list']}>
            <li className={styles['sitemap-list-item']}>
              <Link to="/offres/collectives" className={styles['sitemap-link']}>
                Offres
              </Link>
            </li>
            <li className={styles['sitemap-list-item']}>
              <Link
                to="/reservations/collectives"
                className={styles['sitemap-link']}
              >
                Réservations
              </Link>
            </li>
          </ul>
        </li>
        <li className={styles['sitemap-list-item']}>
          <span className={styles['sitemap-list-title']}>
            Gestion financière
          </span>
          <ul className={styles['sitemap-sub-list']}>
            <li className={styles['sitemap-list-item']}>
              <Link to="/remboursements" className={styles['sitemap-link']}>
                Justificatifs
              </Link>
            </li>
            <li className={styles['sitemap-list-item']}>
              <Link
                to="/remboursements/informations-bancaires"
                className={styles['sitemap-link']}
              >
                Informations bancaires
              </Link>
            </li>
            <li className={styles['sitemap-list-item']}>
              <Link
                to="/remboursements/revenus"
                className={styles['sitemap-link']}
              >
                Chiffre d’affaires
              </Link>
            </li>
          </ul>
        </li>
        <li className={styles['sitemap-list-item']}>
          <Link to="/collaborateurs" className={styles['sitemap-link']}>
            Collaborateurs
          </Link>
        </li>
        <li className={styles['sitemap-list-item']}>
          <Link to="/profil" className={styles['sitemap-link']}>
            Profil
          </Link>
        </li>
      </ul>
    </BasicLayout>
  )
}

// Lazy-loaded by react-router
// ts-unused-exports:disable-next-line
export const Component = Sitemap
