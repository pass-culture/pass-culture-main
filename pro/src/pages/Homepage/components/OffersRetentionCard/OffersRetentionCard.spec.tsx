import { screen } from '@testing-library/react'
import { userEvent } from '@testing-library/user-event'

import { renderWithProviders } from '@/commons/utils/renderWithProviders'

import type { OffersCardVariant } from '../types'
import { OffersRetentionCard } from './OffersRetentionCard'

const FakeCreateOfferPage = ({ variant }: { variant: OffersCardVariant }) => (
  <div>Page création offre {variant.toLowerCase()}</div>
)
const FakeListOffersPage = ({ variant }: { variant: OffersCardVariant }) => (
  <div>Page liste offres {variant.toLowerCase()}</div>
)

const renderOffersRetentionCard = (variant: OffersCardVariant) => {
  const user = userEvent.setup()

  return {
    ...renderWithProviders(null, {
      routes: [
        {
          path: '/',
          element: <OffersRetentionCard variant={variant} />,
        },
        {
          path: '/offre/creation/collectif/vitrine',
          element: <FakeCreateOfferPage variant={'TEMPLATE'} />,
        },
        {
          path: '/offre/creation/collectif',
          element: <FakeCreateOfferPage variant={'BOOKABLE'} />,
        },
        {
          path: '/offre/individuelle/creation/description',
          element: <FakeCreateOfferPage variant={'INDIVIDUAL'} />,
        },
        {
          path: '/offres/vitrines',
          element: <FakeListOffersPage variant={'TEMPLATE'} />,
        },
        {
          path: '/offres/collectives',
          element: <FakeListOffersPage variant={'BOOKABLE'} />,
        },
        {
          path: '/offres',
          element: <FakeListOffersPage variant={'INDIVIDUAL'} />,
        },
      ],
    }),
    user,
  }
}

describe('OffersRetentionCard', () => {
  it('should display template retention card', () => {
    renderOffersRetentionCard('TEMPLATE')

    expect(
      screen.getByRole('heading', {
        level: 2,
        name: 'Activités sur vos offres vitrines',
      })
    ).toBeVisible()
    expect(
      screen.getByText(
        'Aucune nouvelle activité concernant vos offres vitrines'
      )
    ).toBeVisible()
  })

  it('should navigate to template offer creation page', async () => {
    const { user } = renderOffersRetentionCard('TEMPLATE')

    await user.click(
      screen.getByRole('link', { name: 'Créer une offre vitrine' })
    )

    expect(screen.getByText('Page création offre template')).toBeVisible()
  })

  it('should navigate to template offers list page', async () => {
    const { user } = renderOffersRetentionCard('TEMPLATE')

    await user.click(
      screen.getByRole('link', { name: 'Voir toutes les offres' })
    )

    expect(screen.getByText('Page liste offres template')).toBeVisible()
  })

  it('should display bookable retention card', () => {
    renderOffersRetentionCard('BOOKABLE')

    expect(
      screen.getByRole('heading', {
        level: 2,
        name: 'Activités sur vos offres réservables',
      })
    ).toBeVisible()
    expect(
      screen.getByText(
        'Aucune nouvelle activité concernant vos offres réservables'
      )
    ).toBeVisible()
  })

  it('should navigate to bookable offer creation page', async () => {
    const { user } = renderOffersRetentionCard('BOOKABLE')

    await user.click(
      screen.getByRole('link', { name: 'Créer une offre réservable' })
    )

    expect(screen.getByText('Page création offre bookable')).toBeVisible()
  })

  it('should navigate to bookable offers list page', async () => {
    const { user } = renderOffersRetentionCard('BOOKABLE')

    await user.click(
      screen.getByRole('link', { name: 'Voir toutes les offres' })
    )

    expect(screen.getByText('Page liste offres bookable')).toBeVisible()
  })

  it('should display individual retention card', () => {
    renderOffersRetentionCard('INDIVIDUAL')

    expect(
      screen.getByRole('heading', {
        level: 2,
        name: 'Activités sur vos offres individuelles',
      })
    ).toBeVisible()
    expect(
      screen.getByText(
        'Aucune nouvelle activité concernant vos offres individuelles'
      )
    ).toBeVisible()
  })

  it('should navigate to individual offer creation page', async () => {
    const { user } = renderOffersRetentionCard('INDIVIDUAL')

    await user.click(screen.getByRole('link', { name: 'Créer une offre' }))

    expect(screen.getByText('Page création offre individual')).toBeVisible()
  })

  it('should navigate to individual offers list page', async () => {
    const { user } = renderOffersRetentionCard('INDIVIDUAL')

    await user.click(
      screen.getByRole('link', { name: 'Voir toutes les offres' })
    )

    expect(screen.getByText('Page liste offres individual')).toBeVisible()
  })
})
