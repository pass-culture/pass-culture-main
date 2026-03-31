import { screen } from '@testing-library/react'

import { renderWithProviders } from '@/commons/utils/renderWithProviders'

import { OffersCardVariant } from '../types'
import { OffersRetentionCard } from './OffersRetentionCard'

describe('OffersRetentionCard', () => {
  it('should display template retention card', () => {
    renderWithProviders(
      <OffersRetentionCard variant={OffersCardVariant.TEMPLATE} />
    )

    expect(
      screen.getByRole('heading', {
        level: 2,
        name: 'Activités sur vos offres vitrines',
      })
    ).toBeVisible()
    expect(
      screen.getByText(
        'Vous n’avez plus d’offres actives, souhaitez-vous en créer une nouvelle ?'
      )
    ).toBeVisible()
    expect(
      screen.getByRole('link', { name: 'Créer une offre vitrine' })
    ).toHaveAttribute('href', '/offre/creation/collectif/vitrine')
  })

  it('should display bookable retention card', () => {
    renderWithProviders(
      <OffersRetentionCard variant={OffersCardVariant.BOOKABLE} />
    )

    expect(
      screen.getByRole('heading', {
        level: 2,
        name: 'Activités sur vos offres réservables',
      })
    ).toBeVisible()
    expect(
      screen.getByText(
        'Vous n’avez plus d’offres actives, souhaitez-vous en créer une nouvelle ?'
      )
    ).toBeVisible()
    expect(
      screen.getByRole('link', { name: 'Créer une offre réservable' })
    ).toHaveAttribute('href', '/offre/creation/collectif')
  })

  it('should display individual retention card', () => {
    renderWithProviders(
      <OffersRetentionCard variant={OffersCardVariant.INDIVIDUAL} />
    )

    expect(
      screen.getByRole('heading', {
        level: 2,
        name: 'Activités sur vos offres individuelles',
      })
    ).toBeVisible()
    expect(
      screen.getByText(
        'Vous n’avez plus d’offres actives, souhaitez-vous en créer une nouvelle ?'
      )
    ).toBeVisible()
    expect(
      screen.getByRole('link', { name: 'Créer une offre' })
    ).toHaveAttribute('href', '/offre/individuelle/creation/description')
  })
})
