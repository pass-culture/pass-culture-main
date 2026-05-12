import { screen, within } from '@testing-library/react'
import userEvent from '@testing-library/user-event'

import { sharedCurrentUserFactory } from '@/commons/utils/factories/storeFactories'
import {
  type RenderWithProvidersOptions,
  renderWithProviders,
} from '@/commons/utils/renderWithProviders'

import { Sitemap } from './Sitemap'

const renderSitemap = (options: RenderWithProvidersOptions = {}) => {
  return renderWithProviders(<Sitemap />, {
    ...options,
    user: sharedCurrentUserFactory(),
    storeOverrides: {
      user: {
        currentUser: sharedCurrentUserFactory(),
        selectedPartnerVenue: {
          id: 123,
          name: 'Test Venue',
          allowedOnAdage: true,
          hasPartnerPage: true,
        },
      },
      nav: {
        selectedPartnerPageId: '2',
      },
    },
  })
}

const mockNavigate = vi.fn()

vi.mock('react-router', async () => {
  return {
    ...(await vi.importActual('react-router')),
    useNavigate: () => mockNavigate,
  }
})

describe('Sitemap', () => {
  it('should render the sitemap heading', () => {
    renderSitemap()
    expect(
      screen.getByRole('heading', { name: 'Plan du site' })
    ).toBeInTheDocument()
  })

  it('should render all main links in the sitemap', () => {
    renderSitemap()

    const mainLinks = [
      { name: 'Hub', href: '/hub' },
      {
        name: 'Créer une offre',
        href: '/offre/individuelle/creation/description',
      },
      { name: 'Accueil', href: '/accueil' },
      { name: 'Offres', href: '/offres' },
      { name: 'Réservations', href: '/reservations' },
      { name: 'Guichet', href: '/guichet' },
      {
        name: `Page sur l'application (si offre individuelle créée)`,
        href: `/partenaire/page-partenaire`,
      },
      { name: 'Offres vitrines', href: '/offres/vitrines' },
      { name: 'Offres réservables', href: '/offres/collectives' },
      {
        name: `Page sur ADAGE (si validé ADAGE)`,
        href: `/partenaire/page-collective`,
      },
      {
        name: 'Espace administration',
        href: '/administration/remboursements',
      },
      { name: 'Justificatifs', href: '/administration/remboursements' },
      {
        name: 'Informations bancaires',
        href: '/administration/remboursements/informations-bancaires',
      },
      {
        name: 'Chiffre d’affaires',
        href: '/administration/remboursements/revenus',
      },
      { name: 'Individuel', href: '/donnees-activité/individuel' },
      { name: 'Collectif', href: '/donnees-activité/collectif' },
      { name: 'Collaborateurs', href: '/administration/collaborateurs' },
      {
        name: 'Paramètres généraux',
        href: `/partenaire/page-individuelle/parametres`,
      },
      { name: 'Profil', href: '/profil' },
    ]

    const sitemapElement = screen.getByTestId('sitemap')

    mainLinks.forEach((link) => {
      const elements = within(sitemapElement).getAllByRole('link')

      const element = elements.find(
        (el) => el.getAttribute('href') === link.href
      )

      expect(element).toBeInTheDocument()
      expect(element).toHaveAttribute('href', link.href)
    })
  })

  it('should display the back button and return to previous page on click', async () => {
    renderSitemap()

    const retourBtn = screen.getByRole('button', {
      name: 'Retour',
    })
    await userEvent.click(retourBtn)
    expect(mockNavigate).toHaveBeenCalledWith(-1)
  })
})
