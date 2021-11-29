import '@testing-library/jest-dom'
import { render, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { createBrowserHistory } from 'history'
import React from 'react'
import { Router } from 'react-router'

import {
  getCategoriesSelect,
  getSubcategoriesSelect,
  selectOffererAndVenue,
} from '../__tests-utils__/eacOfferCreationUtils'
import setDefaultProps from '../__tests-utils__/setDefaultProps'
import OfferEducational, { IOfferEducationalProps } from '../OfferEducational'

const renderEACOfferCreation = (props: IOfferEducationalProps) => {
  const history = createBrowserHistory()
  return render(
    <Router history={history}>
      <OfferEducational {...props} />
    </Router>
  )
}

describe('screens | OfferEducational', () => {
  let props: IOfferEducationalProps

  beforeEach(() => {
    props = setDefaultProps()
  })

  it('should display empty category', async () => {
    renderEACOfferCreation(props)

    await selectOffererAndVenue()

    const categoriesSelect = getCategoriesSelect()
    expect(categoriesSelect.value).toBe('')

    const subCategoriesSelect = getSubcategoriesSelect()
    expect(subCategoriesSelect).not.toBeInTheDocument()
  })

  it('should update subcategories when category changes', async () => {
    renderEACOfferCreation(props)

    await selectOffererAndVenue()

    const categoriesSelect = getCategoriesSelect()
    userEvent.selectOptions(categoriesSelect, 'CINEMA')
    expect(categoriesSelect.value).toBe('CINEMA')

    const subCategoriesSelect = getSubcategoriesSelect()

    await waitFor(() => expect(subCategoriesSelect.options).toHaveLength(3))

    expect(subCategoriesSelect.value).toBe('')
    expect(subCategoriesSelect.options[0].value).toBe('')
    expect(subCategoriesSelect.options[1].value).toBe('CINE_PLEIN_AIR')
    expect(subCategoriesSelect.options[2].value).toBe('EVENEMENT_CINE')
  })
})
