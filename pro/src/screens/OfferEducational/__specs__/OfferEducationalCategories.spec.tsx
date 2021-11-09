import '@testing-library/jest-dom'
import { render } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { createBrowserHistory } from 'history'
import React from 'react'
import { Router } from 'react-router'


import { getCategoriesSelect, getSubcategoriesSelect } from '../__tests-utils__/eacOfferCreationUtils'
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
  
  it('should display first category and associated subcategories', () => {
    renderEACOfferCreation(props)

    const categoriesSelect = getCategoriesSelect()
    expect(categoriesSelect.value).toBe('MUSEE')

    const subCategoriesSelect = getSubcategoriesSelect()
    expect(subCategoriesSelect.value).toBe('VISITE_GUIDEE')

    expect(subCategoriesSelect.options).toHaveLength(1)
    expect(subCategoriesSelect.options[0].value).toBe('VISITE_GUIDEE')
  })

  it('should update subcategories when category changes', () => {
    renderEACOfferCreation(props)
  
    const categoriesSelect = getCategoriesSelect()
    userEvent.selectOptions(categoriesSelect, 'CINEMA')
    expect(categoriesSelect.value).toBe('CINEMA')

    const subCategoriesSelect = getSubcategoriesSelect()
    expect(subCategoriesSelect.value).toBe('CINE_PLEIN_AIR')

    expect(subCategoriesSelect.options).toHaveLength(2)
    expect(subCategoriesSelect.options[0].value).toBe('CINE_PLEIN_AIR')
    expect(subCategoriesSelect.options[1].value).toBe('EVENEMENT_CINE')
  })
})
