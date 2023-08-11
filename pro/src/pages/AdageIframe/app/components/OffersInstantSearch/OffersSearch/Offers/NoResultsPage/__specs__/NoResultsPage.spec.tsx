import { screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { Formik } from 'formik'
import React from 'react'

import { renderWithProviders } from 'utils/renderWithProviders'

import { SearchFormValues } from '../../../OffersSearch'
import { NoResultsPage } from '../NoResultsPage'

const handleSubmit = vi.fn()
const resetFormMock = vi.fn()

const renderNoResultsPage = ({
  initialValues,
  resetForm,
}: {
  initialValues: SearchFormValues
  resetForm?: () => void
}) => {
  return renderWithProviders(
    <Formik initialValues={initialValues} onSubmit={handleSubmit}>
      <NoResultsPage resetForm={resetForm} />
    </Formik>
  )
}

const initialValues = {
  query: '',
  domains: [],
  students: [],
  eventAddressType: '',
  departments: [],
  academies: [],
  categories: [],
}

describe('ContactButton', () => {
  it('should clear all filters on click button ', async () => {
    renderNoResultsPage({
      initialValues: {
        ...initialValues,
        query: 'test',
        domains: ['test'],
        geolocRadius: 50,
      },
      resetForm: resetFormMock,
    })

    expect(screen.getByText('Aucun résultat trouvé pour cette recherche.'))

    const clearFilterButton = screen.getByRole('button', {
      name: 'Réinitialiser les filtres',
    })
    await userEvent.click(clearFilterButton)

    expect(resetFormMock).toHaveBeenCalled()
  })

  it('should not display clear all filters button ', async () => {
    renderNoResultsPage({
      initialValues: {
        ...initialValues,
        query: '',
        geolocRadius: 50,
      },
    })

    expect(screen.getByText('Aucun résultat trouvé pour cette recherche.'))

    const clearFilterButton = screen.queryByRole('button', {
      name: 'Réinitiliaser les filtres',
    })

    expect(clearFilterButton).not.toBeInTheDocument()
  })
})
