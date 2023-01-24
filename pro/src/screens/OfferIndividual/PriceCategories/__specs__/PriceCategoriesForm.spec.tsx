import '@testing-library/jest-dom'

import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { Formik } from 'formik'
import React from 'react'

import { priceCategoryFormFactory } from '../form/factories'
import { PriceCategoriesFormValues } from '../form/types'
import { PriceCategoriesForm } from '../PriceCategoriesForm'

describe('PriceCategories', () => {
  it('should render without error', () => {
    const values: PriceCategoriesFormValues = {
      priceCategories: [
        priceCategoryFormFactory(),
        priceCategoryFormFactory(),
        priceCategoryFormFactory(),
      ],
      isDuo: false,
    }

    render(
      <Formik initialValues={values} onSubmit={jest.fn()}>
        <PriceCategoriesForm values={values} />
      </Formik>
    )

    expect(screen.getAllByText('Intitulé du tarif')).toHaveLength(3)
  })

  it('should set tarif to 0 when clicking on free checkbox and vice versa', async () => {
    const values: PriceCategoriesFormValues = {
      priceCategories: [
        priceCategoryFormFactory(),
        { ...priceCategoryFormFactory(), price: 0 },
        priceCategoryFormFactory(),
      ],
      isDuo: false,
    }

    render(
      <Formik initialValues={values} onSubmit={jest.fn()}>
        <PriceCategoriesForm values={values} />
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
})
