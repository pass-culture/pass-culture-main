import { useSelector } from 'react-redux'
import { Link } from 'react-router-dom'

import { Layout } from 'app/App/layout/Layout'
import { useActiveFeature } from 'commons/hooks/useActiveFeature'
import { selectCurrentOffererId } from 'commons/store/user/selectors'

import styles from './Sitemap.module.scss'

export const Sitemap = () => {
  const selectedOffererId = useSelector(selectCurrentOffererId)
  const isOffererStatsV2Active = useActiveFeature('WIP_OFFERER_STATS_V2')

  return (
    <Layout>
      <h1 className={styles['title']}>Plan du site</h1>
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
        {!isOffererStatsV2Active && <li className={styles['sitemap-list-item']}>
          <Link to="/statistiques" className={styles['sitemap-link']}>
            Statistiques
          </Link>
        </li>}
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
            {isOffererStatsV2Active && <li className={styles['sitemap-list-item']}>
              <Link
                to="/remboursements/revenus"
                className={styles['sitemap-link']}
              >
                Chiffre d’affaires
              </Link>
            </li>}
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
    </Layout>
  )
}

// Lazy-loaded by react-router-dom
// ts-unused-exports:disable-next-line
export const Component = Sitemap
