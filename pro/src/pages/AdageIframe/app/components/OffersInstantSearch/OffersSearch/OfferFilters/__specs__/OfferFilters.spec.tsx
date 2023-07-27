import { screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { Formik } from 'formik'
import React from 'react'

import * as pcapi from 'pages/AdageIframe/repository/pcapi/pcapi'
import { renderWithProviders } from 'utils/renderWithProviders'

import { SearchFormValues } from '../../OffersSearch'
import { OfferFilters } from '../OfferFilters'

const handleSubmit = vi.fn()
const handleReset = vi.fn()

const renderOfferFilters = ({
  isLoading,
  initialValues,
}: {
  isLoading: boolean
  initialValues: SearchFormValues
}) =>
  renderWithProviders(
    <Formik
      initialValues={initialValues}
      onSubmit={handleSubmit}
      onReset={handleReset}
    >
      <OfferFilters isLoading={isLoading} />
    </Formik>
  )

const initialValues = {
  query: '',
  domains: [],
  students: [],
}

describe('OfferFilters', () => {
  it('renders correctly', () => {
    renderOfferFilters({ isLoading: false, initialValues })

    expect(
      screen.getByPlaceholderText(
        'Rechercher : nom de l’offre, partenaire culturel'
      )
    ).toBeInTheDocument()
    expect(
      screen.getByRole('button', { name: 'Rechercher' })
    ).toBeInTheDocument()
    expect(
      screen.getByRole('button', { name: 'Domaine artistique' })
    ).toBeInTheDocument()
    expect(
      screen.getByRole('button', { name: 'Niveau scolaire' })
    ).toBeInTheDocument()
    expect(
      screen.getByRole('button', { name: 'Effacer les filtres' })
    ).toBeInTheDocument()
  })

  it('should submit onclick search button', async () => {
    renderOfferFilters({ isLoading: false, initialValues })

    await userEvent.click(screen.getByRole('button', { name: 'Rechercher' }))
    expect(handleSubmit).toHaveBeenCalled()
  })

  it('should submit onclick modal search button domain artistic', async () => {
    renderOfferFilters({
      isLoading: false,
      initialValues: {
        ...initialValues,
        domains: [{ value: 'test', label: 'test' }],
      },
    })

    await userEvent.click(
      screen.getByRole('button', { name: 'Domaine artistique (1)' })
    )

    await userEvent.click(screen.getAllByTestId('search-button-modal')[0])

    expect(handleSubmit).toHaveBeenCalled()
  })

  it('should submit onclick modal search button school level', async () => {
    renderOfferFilters({
      isLoading: false,
      initialValues: {
        ...initialValues,
        students: [{ value: 'test', label: 'test' }],
      },
    })

    await userEvent.click(
      screen.getByRole('button', { name: 'Niveau scolaire (1)' })
    )

    await userEvent.click(screen.getAllByTestId('search-button-modal')[1])

    expect(handleSubmit).toHaveBeenCalled()
  })

  it('should reset filter onclick modal clear artistic domain', async () => {
    renderOfferFilters({
      isLoading: false,
      initialValues: {
        ...initialValues,
        domains: [{ value: 'test', label: 'test' }],
      },
    })

    await userEvent.click(
      screen.getByRole('button', { name: 'Domaine artistique (1)' })
    )

    await userEvent.click(screen.getByRole('button', { name: 'Effacer' }))

    expect(
      screen.getByRole('button', { name: 'Domaine artistique' })
    ).toBeInTheDocument()
  })

  it('should reset filter onclick modal clear students', async () => {
    renderOfferFilters({
      isLoading: false,
      initialValues: {
        ...initialValues,
        students: [{ value: 'test', label: 'test' }],
      },
    })

    await userEvent.click(
      screen.getByRole('button', { name: 'Niveau scolaire (1)' })
    )

    await userEvent.click(screen.getByRole('button', { name: 'Effacer' }))

    expect(
      screen.getByRole('button', { name: 'Niveau scolaire' })
    ).toBeInTheDocument()
  })

  it('should return domains options when the api call was successful', async () => {
    vi.spyOn(pcapi, 'getEducationalDomains').mockResolvedValueOnce([
      { id: 1, name: 'Danse' },
      { id: 2, name: 'Architecture' },
      { id: 3, name: 'Arts' },
    ])

    renderOfferFilters({
      isLoading: false,
      initialValues: initialValues,
    })

    await userEvent.click(
      screen.getByRole('button', { name: 'Domaine artistique' })
    )

    expect(screen.getByText('Danse')).toBeInTheDocument()
    expect(screen.getByText('Architecture')).toBeInTheDocument()
    expect(screen.getByText('Arts')).toBeInTheDocument()
  })
})
