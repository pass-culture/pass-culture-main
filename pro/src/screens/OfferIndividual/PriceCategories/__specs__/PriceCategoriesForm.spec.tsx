import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { Formik } from 'formik'
import React from 'react'

import {
  FIRST_INITIAL_PRICE_CATEGORY,
  PRICE_CATEGORY_MAX_LENGTH,
} from '../form/constants'
import { priceCategoryFormFactory } from '../form/factories'
import { PriceCategoriesFormValues } from '../form/types'
import { PriceCategoriesForm } from '../PriceCategoriesForm'

const defaultValues: PriceCategoriesFormValues = {
  priceCategories: [
    priceCategoryFormFactory(),
    priceCategoryFormFactory(),
    priceCategoryFormFactory(),
  ],
  isDuo: false,
}

const renderPriceCategoriesForm = (
  customValues?: Partial<PriceCategoriesFormValues>
) => {
  const values = { ...defaultValues, ...customValues }
  return render(
    <Formik initialValues={values} onSubmit={jest.fn()}>
      <PriceCategoriesForm />
    </Formik>
  )
}

describe('PriceCategories', () => {
  it('should render without error', () => {
    renderPriceCategoriesForm()

    expect(screen.getAllByText('Intitulé du tarif')).toHaveLength(3)
  })

  it('should set tarif to 0 when clicking on free checkbox and vice versa', async () => {
    const values: PriceCategoriesFormValues = {
      priceCategories: [
        priceCategoryFormFactory(),
        priceCategoryFormFactory({ price: 0 }),
        priceCategoryFormFactory(),
      ],
      isDuo: false,
    }

    render(
      <Formik initialValues={values} onSubmit={jest.fn()}>
        <PriceCategoriesForm />
      </Formik>
    )

    const freeCheckboxes = screen.getAllByLabelText('Gratuit')

    // I check initial values
    expect(freeCheckboxes[0]).not.toBeChecked()
    expect(freeCheckboxes[1]).toBeChecked()
    expect(freeCheckboxes[2]).not.toBeChecked()

    // I checked all checkboxes are checked
    await userEvent.click(freeCheckboxes[0])
    await userEvent.click(freeCheckboxes[2])

    expect(freeCheckboxes[0]).toBeChecked()
    expect(freeCheckboxes[1]).toBeChecked()
    expect(freeCheckboxes[2]).toBeChecked()

    const tarifFields = screen.getAllByLabelText('Tarif par personne')
    expect(tarifFields[0]).toHaveValue(0)
    expect(tarifFields[1]).toHaveValue(0)
    expect(tarifFields[2]).toHaveValue(0)

    // I set prices checkboxes are unchecked
    await userEvent.type(tarifFields[0], '20')
    await userEvent.type(tarifFields[1], '21')
    await userEvent.type(tarifFields[2], '0.1')

    expect(freeCheckboxes[0]).not.toBeChecked()
    expect(freeCheckboxes[1]).not.toBeChecked()
    expect(freeCheckboxes[2]).not.toBeChecked()
  })

  it('should not let add more than 20 price categories', async () => {
    renderPriceCategoriesForm({ priceCategories: [priceCategoryFormFactory()] })

    for (let i = 0; i < PRICE_CATEGORY_MAX_LENGTH - 1; i++) {
      await userEvent.click(screen.getByText('Ajouter un tarif'))
    }

    expect(screen.getAllByText('Intitulé du tarif')).toHaveLength(
      PRICE_CATEGORY_MAX_LENGTH
    )
    expect(screen.getByText('Ajouter un tarif')).toBeDisabled()
  })

  it('should remove price categories on trash button click', async () => {
    renderPriceCategoriesForm()

    expect(
      screen.getAllByRole('button', { name: 'Supprimer le tarif' })[0]
    ).toBeEnabled()
    await userEvent.click(
      screen.getAllByRole('button', { name: 'Supprimer le tarif' })[0]
    )
    await userEvent.click(
      screen.getAllByRole('button', { name: 'Supprimer le tarif' })[0]
    )
    expect(
      screen.getAllByRole('button', { name: 'Supprimer le tarif' })[0]
    ).toBeDisabled()
  })

  it('should handle unique line label cases', async () => {
    renderPriceCategoriesForm({
      priceCategories: [FIRST_INITIAL_PRICE_CATEGORY],
    })

    // one price category line : label is default and field is disable
    expect(
      screen.getAllByRole('button', { name: 'Supprimer le tarif' })[0]
    ).toBeDisabled()
    expect(screen.getByDisplayValue('Tarif unique')).toBeDisabled()

    // I add a price category line
    await userEvent.click(screen.getByText('Ajouter un tarif'))
    const nameFields = screen.getAllByLabelText('Intitulé du tarif')
    expect(nameFields[0]).toHaveValue('')
    expect(nameFields[0]).not.toBeDisabled()

    // I change the label and remove last line, label is default and field disable
    await userEvent.type(nameFields[0], 'Tarif Koala')
    await userEvent.click(
      screen.getAllByRole('button', { name: 'Supprimer le tarif' })[1]
    )
    expect(nameFields[0]).toHaveValue('Tarif unique')
    expect(nameFields[0]).toBeDisabled()
  })
})
