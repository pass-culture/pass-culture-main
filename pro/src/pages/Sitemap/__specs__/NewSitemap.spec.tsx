import { screen, within } from '@testing-library/react'
import userEvent from '@testing-library/user-event'

import {
  currentOffererFactory,
  sharedCurrentUserFactory,
} from '@/commons/utils/factories/storeFactories'
import {
  type RenderWithProvidersOptions,
  renderWithProviders,
} from '@/commons/utils/renderWithProviders'

import { NewSitemap } from '../NewSitemap'

const renderNewSitemap = (options: RenderWithProvidersOptions = {}) => {
  return renderWithProviders(<NewSitemap />, {
    ...options,
    user: sharedCurrentUserFactory(),
    storeOverrides: {
      user: {
        currentUser: sharedCurrentUserFactory(),
        selectedVenue: {
          id: 123,
          name: 'Test Venue',
          allowedOnAdage: true,
          hasPartnerPage: true,
        },
      },
      offerer: currentOffererFactory({ currentOfferer: { id: 42 } }),
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
    renderNewSitemap()
    expect(
      screen.getByRole('heading', { name: 'Plan du site' })
    ).toBeInTheDocument()
  })

  it('should render all main links in the sitemap', () => {
    renderNewSitemap()

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
        href: `/structures/42/lieux/2/page-partenaire`,
      },
      { name: 'Offres vitrines', href: '/offres/vitrines' },
      { name: 'Offres réservables', href: '/offres/collectives' },
      {
        name: `Page sur ADAGE (si validé ADAGE)`,
        href: `/structures/42/lieux/123/collectif`,
      },
      {
        name: 'Espace administration',
        href: '/remboursements',
      },
      { name: 'Justificatifs', href: '/remboursements' },
      {
        name: 'Informations bancaires',
        href: '/remboursements/informations-bancaires',
      },
      { name: 'Chiffre d’affaires', href: '/remboursements/revenus' },
      { name: 'Individuel', href: '/donnees-activité/individuel' },
      { name: 'Collectif', href: '/donnees-activité/collectif' },
      { name: 'Collaborateurs', href: '/collaborateurs' },
      {
        name: 'Paramètres généraux',
        href: `/structures/42/lieux/123/parametres`,
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
    renderNewSitemap()

    const retourBtn = screen.getByRole('button', {
      name: 'Retour',
    })
    await userEvent.click(retourBtn)
    expect(mockNavigate).toHaveBeenCalledWith(-1)
  })
})
