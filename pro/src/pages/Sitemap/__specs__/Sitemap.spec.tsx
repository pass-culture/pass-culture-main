import { screen, within } from '@testing-library/react'
import * as reactRedux from 'react-redux'

import { renderWithProviders } from 'utils/renderWithProviders'

import { Sitemap } from '../Sitemap'

vi.mock('react-redux', async () => {
  const originalModule = await vi.importActual('react-redux')
  return {
    ...originalModule,
    useSelector: vi.fn(),
  }
})

const renderSitemap = () => {
  return renderWithProviders(<Sitemap />)
}

describe('Sitemap', () => {
  beforeEach(() => {
    vi.spyOn(reactRedux, 'useSelector').mockReturnValue(42)
  })

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
      { name: 'Statistiques', href: '/statistiques' },
      { name: 'Justificatifs', href: '/remboursements' },
      {
        name: 'Informations bancaires',
        href: '/remboursements/informations-bancaires',
      },
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
})
