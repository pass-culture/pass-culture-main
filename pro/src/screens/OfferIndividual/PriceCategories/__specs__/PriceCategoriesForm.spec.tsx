import { render, screen } from '@testing-library/react'
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
})
