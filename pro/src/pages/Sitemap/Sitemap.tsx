import { useTranslation } from 'react-i18next'
import { useSelector } from 'react-redux'
import { Link } from 'react-router-dom'

import { AppLayout } from 'app/AppLayout'
import { selectCurrentOffererId } from 'store/user/selectors'

import styles from './Sitemap.module.scss'

export const Sitemap = () => {
  const { t } = useTranslation('common')
  const selectedOffererId = useSelector(selectCurrentOffererId)

  return (
    <AppLayout>
      <h1 className={styles['title']}>{t('site_map')}</h1>
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
          <span className={styles['sitemap-list-title']}>
            {t('individual')}
          </span>
          <ul className={styles['sitemap-sub-list']}>
            <li className={styles['sitemap-list-item']}>
              <Link to="/offres" className={styles['sitemap-link']}>
                {t('offers')}
              </Link>
            </li>
            <li className={styles['sitemap-list-item']}>
              <Link to="/reservations" className={styles['sitemap-link']}>
                {t('reservations')}
              </Link>
            </li>
            <li className={styles['sitemap-list-item']}>
              <Link to="/guichet" className={styles['sitemap-link']}>
                {t('ticket_office')}
              </Link>
            </li>
          </ul>
        </li>

        <li className={styles['sitemap-list-item']}>
          <span className={styles['sitemap-list-title']}>
            {t('collective')}
          </span>
          <ul className={styles['sitemap-sub-list']}>
            <li className={styles['sitemap-list-item']}>
              <Link to="/offres/collectives" className={styles['sitemap-link']}>
                {t('offers')}
              </Link>
            </li>
            <li className={styles['sitemap-list-item']}>
              <Link
                to="/reservations/collectives"
                className={styles['sitemap-link']}
              >
                {t('reservations')}
              </Link>
            </li>
          </ul>
        </li>
        <li className={styles['sitemap-list-item']}>
          <Link to="/statistiques" className={styles['sitemap-link']}>
            {t('statistics')}
          </Link>
        </li>
        <li className={styles['sitemap-list-item']}>
          <span className={styles['sitemap-list-title']}>
            {t('financial_management')}
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
          </ul>
        </li>
        <li className={styles['sitemap-list-item']}>
          <Link to="/collaborateurs" className={styles['sitemap-link']}>
            {t('collaborators')}
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
