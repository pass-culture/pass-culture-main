import React from 'react'
import { NavLink } from 'react-router-dom'

import { AppLayout } from 'app/AppLayout'
import useCurrentUser from 'hooks/useCurrentUser'

import styles from './Sitemap.module.scss'

export const Sitemap = () => {
  const { selectedOffererId } = useCurrentUser()
  return (
    <AppLayout>
      <h1>Plan du site</h1>
      <ul className={styles['sitemap-list']}>
        <li className={styles['sitemap-list-item']}>
          <NavLink to="/accueil" className={styles['sitemap-link']}>
            Accueil
          </NavLink>
          <ul className={styles['sitemap-sub-list']}>
            <li className={styles['sitemap-list-item']}>
              <NavLink
                to={`/structures/${selectedOffererId}`}
                className={styles['sitemap-link']}
              >
                Structure
              </NavLink>
            </li>
            <li className={styles['sitemap-list-item']}>
              <NavLink
                to={`/offre/creation?structure=${selectedOffererId}`}
                className={styles['sitemap-link']}
              >
                Créer une offre
              </NavLink>
            </li>
            <li className={styles['sitemap-list-item']}>
              <NavLink to="/profil" className={styles['sitemap-link']}>
                Profil
              </NavLink>
            </li>
          </ul>
        </li>
        <li className={styles['sitemap-list-item']}>
          <NavLink to="/guichet" className={styles['sitemap-link']}>
            Guichet
          </NavLink>
        </li>

        <li className={styles['sitemap-list-item']}>
          <span className={styles['sitemap-list-title']}>Offres</span>
          <ul className={styles['sitemap-sub-list']}>
            <li className={styles['sitemap-list-item']}>
              <NavLink to="/offres" className={styles['sitemap-link']}>
                Offres individuelles
              </NavLink>
            </li>
            <li className={styles['sitemap-list-item']}>
              <NavLink
                to="/offres/collectives"
                className={styles['sitemap-link']}
              >
                Offres collectives
              </NavLink>
            </li>
          </ul>
        </li>
        <li className={styles['sitemap-list-item']}>
          <span className={styles['sitemap-list-title']}>Réservations</span>
          <ul className={styles['sitemap-sub-list']}>
            <li className={styles['sitemap-list-item']}>
              <NavLink to="/reservations" className={styles['sitemap-link']}>
                Réservations individuelles
              </NavLink>
            </li>
            <li className={styles['sitemap-list-item']}>
              <NavLink
                to="/reservations/collectives"
                className={styles['sitemap-link']}
              >
                Réservations collectives
              </NavLink>
            </li>
          </ul>
        </li>
        <li className={styles['sitemap-list-item']}>
          <span className={styles['sitemap-list-title']}>
            Gestion financière
          </span>
          <ul className={styles['sitemap-sub-list']}>
            <li className={styles['sitemap-list-item']}>
              <NavLink to="/remboursements" className={styles['sitemap-link']}>
                Justificatifs
              </NavLink>
            </li>
            <li className={styles['sitemap-list-item']}>
              <NavLink
                to="/remboursements/details"
                className={styles['sitemap-link']}
              >
                Détails
              </NavLink>
            </li>
            <li className={styles['sitemap-list-item']}>
              <NavLink
                to="/remboursements/informations-bancaires"
                className={styles['sitemap-link']}
              >
                Informations bancaires
              </NavLink>
            </li>
          </ul>
        </li>
        <li className={styles['sitemap-list-item']}>
          <NavLink to="/statistiques" className={styles['sitemap-link']}>
            Statistiques
          </NavLink>
        </li>
      </ul>
    </AppLayout>
  )
}

// Lazy-loaded by react-router-dom
// ts-unused-exports:disable-next-line
export const Component = Sitemap
