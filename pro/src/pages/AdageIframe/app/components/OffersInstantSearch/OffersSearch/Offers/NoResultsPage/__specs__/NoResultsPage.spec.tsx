import { screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { Formik } from 'formik'
import React from 'react'

import { renderWithProviders } from 'utils/renderWithProviders'

import { SearchFormValues } from '../../../OffersSearch'
import { NoResultsPage } from '../NoResultsPage'

const handleSubmit = jest.fn()
const handleReset = jest.fn()

const renderNoResultsPage = ({
  initialValues,
}: {
  initialValues: SearchFormValues
}) => {
  return renderWithProviders(
    <Formik
      initialValues={initialValues}
      onSubmit={handleSubmit}
      onReset={handleReset}
    >
      <NoResultsPage />
    </Formik>
  )
}

const initialValues = {
  query: '',
  domains: [],
  students: [],
}

describe('ContactButton', () => {
  it('should clear all filters on click button ', async () => {
    renderNoResultsPage({
      initialValues: {
        ...initialValues,
        query: 'test',
        domains: [{ value: 'test', label: 'test' }],
      },
    })

    expect(screen.getByText('Aucun résultat trouvé pour cette recherche.'))

    const clearFilterButton = screen.getByRole('button', {
      name: 'Effacer les filtres',
    })
    await userEvent.click(clearFilterButton)

    expect(handleReset).toHaveBeenCalled()
  })

  it('should not display clear all filters button ', async () => {
    renderNoResultsPage({
      initialValues: {
        ...initialValues,
        query: '',
      },
    })

    expect(screen.getByText('Aucun résultat trouvé pour cette recherche.'))

    const clearFilterButton = screen.queryByRole('button', {
      name: 'Effacer les filtres',
    })

    expect(clearFilterButton).not.toBeInTheDocument()
  })
})
