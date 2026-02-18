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

import { Sitemap } from '../Sitemap'

const renderSitemap = (options: RenderWithProvidersOptions = {}) => {
  return renderWithProviders(<Sitemap />, {
    ...options,
    user: sharedCurrentUserFactory(),
    storeOverrides: {
      user: { currentUser: sharedCurrentUserFactory() },
      offerer: currentOffererFactory({ currentOfferer: { id: 42 } }),
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
      { name: 'Créer une offre', href: '/offre/creation?structure=42' },
      { name: 'Accueil', href: '/accueil' },
      { name: 'Offres', href: '/offres' },
      { name: 'Réservations', href: '/reservations' },
      { name: 'Guichet', href: '/guichet' },
      { name: 'Offres', href: '/offres/collectives' },
      { name: 'Réservations', href: '/reservations/collectives' },
      { name: 'Justificatifs', href: '/remboursements' },
      {
        name: 'Informations bancaires',
        href: '/remboursements/informations-bancaires',
      },
      { name: 'Justificatifs', href: '/remboursements/revenus' },
      { name: 'Collaborateurs', href: '/collaborateurs' },
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

  it('should render all section titles in the sitemap', () => {
    renderSitemap()

    const sectionTitles = ['Individuel', 'Collectif', 'Gestion financière']

    const sitemapElement = screen.getByTestId('sitemap')

    sectionTitles.forEach((title) => {
      const element = within(sitemapElement).getByText(title)
      expect(element).toBeInTheDocument()
    })
  })

  it('should render nested links correctly', () => {
    renderSitemap()

    const nestedLinks = [
      { parent: 'Individuel', name: 'Offres', href: '/offres' },
      { parent: 'Individuel', name: 'Réservations', href: '/reservations' },
      { parent: 'Individuel', name: 'Guichet', href: '/guichet' },
      { parent: 'Collectif', name: 'Offres', href: '/offres/collectives' },
      {
        parent: 'Collectif',
        name: 'Réservations',
        href: '/reservations/collectives',
      },
      {
        parent: 'Gestion financière',
        name: 'Justificatifs',
        href: '/remboursements',
      },
      {
        parent: 'Gestion financière',
        name: 'Informations bancaires',
        href: '/remboursements/informations-bancaires',
      },
    ]

    const sitemapElement = screen.getByTestId('sitemap')

    nestedLinks.forEach((link) => {
      const parentElement = within(sitemapElement).getByText(link.parent)
      const parentListItem = parentElement.closest('li')
      if (parentListItem) {
        const nestedElement = within(parentListItem).getByRole('link', {
          name: link.name,
        })
        expect(nestedElement).toBeInTheDocument()
        expect(nestedElement).toHaveAttribute('href', link.href)
      }
    })
  })

  it('should render the revenue page nested link in "Gestion financière" list', () => {
    renderSitemap()

    const sitemapElement = screen.getByTestId('sitemap')
    const element = within(sitemapElement).getByRole('link', {
      name: 'Chiffre d’affaires',
    })

    expect(element).toBeInTheDocument()
    expect(element).toHaveAttribute('href', '/remboursements/revenus')
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
