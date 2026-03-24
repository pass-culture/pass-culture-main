import { screen } from '@testing-library/react'

import { renderWithProviders } from '@/commons/utils/renderWithProviders'

import { OffersEmptyStateCardVariant } from '../types'
import { OffersEmptyStateCard } from './OffersEmptyStateCard'

it('should display correct information when variant is BOOKABLE', () => {
  renderWithProviders(
    <OffersEmptyStateCard variant={OffersEmptyStateCardVariant.BOOKABLE} />
  )

  expect(
    screen.getByRole('heading', {
      name: 'Adresser une offre réservable à un établissement scolaire',
    })
  ).toBeVisible()

  expect(
    screen.getByText(
      'L’offre réservable, datée et tarifée, est destinée à un seul établissement scolaire pour que le projet que vous avez co-construit ensemble puisse se réaliser.'
    )
  ).toBeVisible()

  expect(
    screen.getByRole('link', { name: 'Créer une offre réservable' })
  ).toHaveAttribute('href', '/offre/creation/collectif')
})

it('should display correct information when variant is TEMPLATE', () => {
  renderWithProviders(
    <OffersEmptyStateCard variant={OffersEmptyStateCardVariant.TEMPLATE} />
  )

  expect(
    screen.getByRole('heading', {
      name: 'Rendre vos offres visibles à tous les établissements scolaires sur ADAGE',
    })
  ).toBeVisible()

  expect(
    screen.getByText(
      "Les offres vitrines vous permettent de présenter vos propositions aux enseignants afin qu'ils puissent vous contacter pour co-construire des projets d'éducation artistique et culturelle."
    )
  ).toBeVisible()

  expect(
    screen.getByRole('link', { name: 'Créer une offre vitrine' })
  ).toHaveAttribute('href', '/offre/creation/collectif/vitrine')
})

it('should display correct information when variant is INDIVIDUAL', () => {
  renderWithProviders(
    <OffersEmptyStateCard variant={OffersEmptyStateCardVariant.INDIVIDUAL} />
  )

  expect(
    screen.getByRole('heading', {
      name: 'Proposer vos offres sur l’application mobile pass Culture',
    })
  ).toBeVisible()

  expect(
    screen.getByText(
      "Les offres individuelles vous permettent de présenter vos propositions culturelles sur l'application."
    )
  ).toBeVisible()

  expect(
    screen.getByRole('link', { name: 'Créer une offre individuelle' })
  ).toHaveAttribute('href', '/offre/individuelle/creation/description')
})
