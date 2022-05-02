import '@testing-library/jest-dom'
import { render, screen } from '@testing-library/react'
import { Provider } from 'react-redux'
import { Formik } from 'formik'
import React from 'react'
import * as yup from 'yup'

import { configureTestStore } from 'store/testUtils'
import Categories from '../Categories'
import { Category, SubCategory } from 'custom_types/categories'

import { validationSchema }  from '..'
import { MemoryRouter } from 'react-router-dom'

interface ICategoriesProps {
  categories: Category[]
  subcategories: SubCategory[]
}

interface IInitialValues {
  categoryId: string
  subcategoryId: string
  musicType: string
  musicSubType: string
  showType: string
  showSubType: string
}

const renderCategories = ({
  initialValues,
  onSubmit = jest.fn(),
  props,
}: {
  initialValues: IInitialValues
  onSubmit: () => void
  props: ICategoriesProps
}) => {
  const store = configureTestStore({
    data: { offers: [{ categories: [] }] },
  })
  return render(
    <Provider store={store}>
      <MemoryRouter>
        <Formik
          initialValues={initialValues}
          onSubmit={onSubmit}
          validationSchema={yup.object().shape(validationSchema)}
          >
          <Categories {...props} />
        </Formik>
      </MemoryRouter>
    </Provider>
  )
}

describe('OfferIndividual section: Categories', () => {
  let initialValues: IInitialValues
  let onSubmit = jest.fn()
  let props: ICategoriesProps

  beforeEach(() => {
    initialValues = {
      categoryId: '',
      subcategoryId: '',
      musicType: '',
      musicSubType: '',
      showType: '',
      showSubType: '',
    }

    props = {categories: [], subcategories: []}
  })

  it('should render the component', async () => {
    renderCategories({
      initialValues,
      onSubmit,
      props
    })
    expect(
      await screen.findByText('Type d’offre')
    ).toBeInTheDocument()
  })
})