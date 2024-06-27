import { useSelector } from 'react-redux'
import { Link } from 'react-router-dom'

import { AppLayout } from 'app/AppLayout'
import { selectCurrentOffererId } from 'store/user/selectors'

import styles from './Sitemap.module.scss'

export const Sitemap = () => {
  const selectedOffererId = useSelector(selectCurrentOffererId)

  return (
    <AppLayout>
      <h1>Plan du site</h1>
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
          <Link to="/statistiques" className={styles['sitemap-link']}>
            Statistiques
          </Link>
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
                to="/remboursements/details"
                className={styles['sitemap-link']}
              >
                Détails
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
    </AppLayout>
  )
}

// Lazy-loaded by react-router-dom
// ts-unused-exports:disable-next-line
export const Component = Sitemap
