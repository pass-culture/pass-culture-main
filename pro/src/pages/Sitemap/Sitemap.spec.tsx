import { screen, within } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { axe } from 'vitest-axe'

import { sharedCurrentUserFactory } from '@/commons/utils/factories/storeFactories'
import {
  type RenderWithProvidersOptions,
  renderWithProviders,
} from '@/commons/utils/renderWithProviders'

import { Sitemap } from './Sitemap'

const renderSitemap = (
  isSettlementEnable = false,
  options: RenderWithProvidersOptions = {}
) => {
  return renderWithProviders(<Sitemap />, {
    ...options,
    features: isSettlementEnable ? ['WIP_ENABLE_FINANCE_SETTLEMENTS'] : [],
    user: sharedCurrentUserFactory(),
    storeOverrides: {
      user: {
        currentUser: sharedCurrentUserFactory(),
        selectedPartnerVenue: {
          id: 123,
          name: 'Test Venue',
          allowedOnAdage: true,
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
  it('should render without accessibility violations', async () => {
    const { container } = renderSitemap()

    expect(await axe(container)).toHaveNoViolations()
  })

  it('should render the sitemap heading', () => {
    renderSitemap()
    expect(
      screen.getByRole('heading', { name: 'Plan du site' })
    ).toBeInTheDocument()
  })

  it.each([true, false])(
    'should render all main links in the sitemap when settlements are %s',
    (isSettlementEnable) => {
      renderSitemap(isSettlementEnable)

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
          href: '/administration/gestion-financiere',
        },
        {
          name: 'Justificatifs',
          href: '/administration/gestion-financiere/justificatifs',
        },
        ...(isSettlementEnable
          ? [
              {
                name: 'Virements',
                href: '/administration/gestion-financiere/virements',
              },
            ]
          : []),
        {
          name: 'Informations bancaires',
          href: '/administration/gestion-financiere/informations-bancaires',
        },
        {
          name: 'Chiffre d’affaires',
          href: '/administration/gestion-financiere/chiffre-d-affaires',
        },
        {
          name: 'Individuel',
          href: '/administration/donnees-activite/individuel',
        },
        {
          name: 'Collectif',
          href: '/administration/donnees-activite/collectif',
        },
        { name: 'Collaborateurs', href: '/administration/collaborateurs' },
        {
          name: 'Paramètres',
          href: `/parametres`,
        },
        { name: 'Profil', href: '/profil' },
      ]

      const elements = within(screen.getByTestId('sitemap')).getAllByRole(
        'link'
      )
      mainLinks.forEach((link) => {
        const element = elements.find(
          (el) => el.getAttribute('href') === link.href
        )

        expect(element).toBeInTheDocument()
        expect(element).toHaveAttribute('href', link.href)
      })
    }
  )

  it('should display the back button and return to previous page on click', async () => {
    renderSitemap()

    const retourBtn = screen.getByRole('button', {
      name: 'Retour',
    })
    await userEvent.click(retourBtn)
    expect(mockNavigate).toHaveBeenCalledWith(-1)
  })
})
