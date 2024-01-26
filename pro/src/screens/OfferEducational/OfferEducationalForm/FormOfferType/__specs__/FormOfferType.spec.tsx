import { screen } from '@testing-library/react'
import { Formik } from 'formik'

import { renderWithProviders } from 'utils/renderWithProviders'

import FormOfferType, { FormTypeProps } from '../FormOfferType'

const formTypeProps: FormTypeProps = {
  categories: [],
  disableForm: false,
  domainsOptions: [],
  nationalPrograms: [],
  subCategories: [],
}

function renderFormOfferType(props: FormTypeProps) {
  return renderWithProviders(
    <Formik initialValues={{ title: '', domains: [] }} onSubmit={vi.fn()}>
      {({ handleSubmit }) => (
        <form onSubmit={handleSubmit}>
          <FormOfferType {...props} />
        </form>
      )}
    </Formik>
  )
}

describe('FormOfferType', () => {
  it('should render the form description', async () => {
    renderFormOfferType(formTypeProps)
    expect(
      await screen.findByText(
        'Le type de l’offre permet de la caractériser et de la valoriser au mieux pour les enseignants et chefs d’établissement.'
      )
    ).toBeInTheDocument()
  })

  it('should offer the national program oprtions filtered for the selected domains', async () => {
    renderFormOfferType({
      ...formTypeProps,
      nationalPrograms: [
        { value: 4, label: 'Program 1' }, //  Program with id 4 should be displayed whatever the domain selection is
        { value: 11, label: 'Program 2' },
      ],
      domainsOptions: [],
    })

    expect(
      await screen.findByRole('option', { name: 'Program 1' })
    ).toBeInTheDocument()

    expect(
      screen.queryByRole('option', { name: 'Program 2' })
    ).not.toBeInTheDocument()
  })
})
