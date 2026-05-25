import { Link, useNavigate } from 'react-router'

import { BasicLayout } from '@/app/App/layouts/BasicLayout/BasicLayout'
import { useAppSelector } from '@/commons/hooks/useAppSelector'
import { Button } from '@/design-system/Button/Button'
import {
  ButtonColor,
  ButtonVariant,
  IconPositionEnum,
} from '@/design-system/Button/types'
import fullBackIcon from '@/icons/full-back.svg'

import styles from './Sitemap.module.scss'

interface SitemapLink {
  title: string
  path: string | null
  children: SitemapLink[]
  hidden?: boolean
}

export const Sitemap = () => {
  const navigate = useNavigate()
  const selectedPartnerVenue = useAppSelector(
    (state) => state.user.selectedPartnerVenue
  )

  const sitemapLinks: SitemapLink[] = [
    {
      title: 'Hub',
      path: '/hub',
      children: [],
    },
    {
      title: 'Accueil',
      path: '/accueil',
      children: [
        {
          title: 'Créer une offre',
          path: `/offre/individuelle/creation/description`,
          children: [],
        },
        {
          title: 'Individuel',
          path: null,
          children: [
            { title: 'Offres', path: '/offres', children: [] },
            { title: 'Réservations', path: '/reservations', children: [] },
            { title: 'Guichet', path: '/guichet', children: [] },
            {
              title: "Page sur l'application (si offre individuelle créée)",
              path: `/partenaire/page-partenaire`,
              hidden: !selectedPartnerVenue?.hasPartnerPage,
              children: [],
            },
          ],
        },
        {
          title: 'Collectif',
          path: null,
          children: [
            {
              title: 'Offres vitrines',
              path: '/offres/vitrines',
              children: [],
            },
            {
              title: 'Offres réservables',
              path: '/offres/collectives',
              children: [],
            },
            {
              title: 'Page sur ADAGE (si validé ADAGE)',
              path: `/partenaire/page-collective`,
              hidden: !selectedPartnerVenue?.allowedOnAdage,
              children: [],
            },
          ],
        },
      ],
    },
    {
      title: 'Espace administration',
      path: '/administration/remboursements',
      children: [
        {
          title: 'Gestion financière',
          path: null,
          children: [
            {
              title: 'Justificatifs',
              path: '/administration/remboursements',
              children: [],
            },
            {
              title: 'Informations bancaires',
              path: '/administration/remboursements/informations-bancaires',
              children: [],
            },
            {
              title: 'Chiffre d’affaires',
              path: '/administration/remboursements/revenus',
              children: [],
            },
          ],
        },
        {
          title: "Données d'activité",
          path: null,
          children: [
            {
              title: 'Individuel',
              path: '/donnees-activité/individuel',
              children: [],
            },
            {
              title: 'Collectif',
              path: '/donnees-activité/collectif',
              children: [],
            },
          ],
        },
      ],
    },
    {
      title: 'Collaborateurs',
      path: '/administration/collaborateurs',
      children: [],
    },
    {
      title: 'Paramètres',
      path: `/parametres`,
      children: [],
    },
    {
      title: 'Profil',
      path: '/profil',
      children: [],
    },
  ]
  const renderSitemapItems = (items: SitemapLink[]) => {
    return items
      .filter((item) => !item.hidden)
      .map((link) => (
        <li
          key={link.path ?? link.title}
          className={styles['sitemap-list-item']}
        >
          {link.path ? (
            <Link
              to={link.path}
              className={
                link.children.length > 0
                  ? styles['sitemap-section-link']
                  : styles['sitemap-link']
              }
            >
              {link.title}
            </Link>
          ) : (
            <span className={styles['sitemap-list-subtitle']}>
              {link.title}
            </span>
          )}

          {link.children.length > 0 && (
            <ul className={styles['sitemap-sub-list']}>
              {renderSitemapItems(link.children)}
            </ul>
          )}
        </li>
      ))
  }

  return (
    <BasicLayout mainHeading="Plan du site" isFullPage={true}>
      <Button
        onClick={() => navigate(-1)}
        color={ButtonColor.NEUTRAL}
        variant={ButtonVariant.TERTIARY}
        icon={fullBackIcon}
        iconPosition={IconPositionEnum.LEFT}
        label="Retour"
      />
      <ul className={styles['sitemap-list']} data-testid="sitemap">
        {renderSitemapItems(sitemapLinks)}
      </ul>
    </BasicLayout>
  )
}

// Lazy-loaded by react-router
// ts-unused-exports:disable-next-line
export const Component = Sitemap
