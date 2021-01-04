import { fireEvent } from '@testing-library/dom'
import '@testing-library/jest-dom'
import { act, render, screen } from '@testing-library/react'
import moment from 'moment'
import React, { Fragment } from 'react'
import { Provider } from 'react-redux'

import NotificationV2Container from 'components/layout/NotificationV2/NotificationV2Container'
import * as pcapi from 'repository/pcapi/pcapi'
import { configureTestStore } from 'store/testUtils'

import StockItemContainer from './StockItemContainer'

jest.mock('repository/pcapi/pcapi', () => ({
  updateStock: jest.fn(),
}))

const renderStockItem = (props, store) =>
  act(async () => {
    await render(
      <Provider store={store}>
        <Fragment>
          <table>
            <tbody>
              <StockItemContainer {...props} />
            </tbody>
          </table>
          <NotificationV2Container />
        </Fragment>
      </Provider>
    )
  })

describe('stocks page', () => {
  let props
  let store
  beforeEach(() => {
    store = configureTestStore({ data: { users: [{ publicName: 'François', isAdmin: false }] } })
    jest.spyOn(Date.prototype, 'toISOString').mockImplementation(() => '2020-12-15T12:00:00Z')

    props = {
      departmentCode: '986',
      isEvent: true,
      isOfferSynchronized: false,
      refreshOffer: jest.fn(),
      setParentIsEditing: jest.fn(),
      stock: {
        id: 'AA',
        bookingsQuantity: 1,
        isEventDeletable: true,
        beginningDatetime: moment().add(5, 'days').format(),
        bookingLimitDatetime: null,
        price: 10,
        quantity: 20,
      },
    }
  })

  afterEach(() => {
    pcapi.updateStock.mockReset()
  })

  describe('render', () => {
    it('should display error message on api error', async () => {
      // Given
      pcapi.updateStock.mockRejectedValue({
        errors: {
          price: 'Price error.',
          quantity: 'Quantity error.',
        },
      })

      await renderStockItem(props, store)
      const modifyButton = screen.getByAltText('Modifier le stock').closest('button')
      fireEvent.click(modifyButton)
      const submitIcon = await screen.findByAltText('Valider les modifications')
      const submitButton = submitIcon.closest('button')
      // When
      fireEvent.click(submitButton)

      // Then
      const errorMessage = await screen.findByText('Impossible de modifier le stock.', {
        exact: false,
      })
      expect(errorMessage).toBeInTheDocument()
      const priceErrorMessage = await screen.findByText('Price error.', {
        exact: false,
      })
      expect(priceErrorMessage).toBeInTheDocument()
      const quantityErrorMessage = await screen.findByText('Quantity error.', {
        exact: false,
      })
      expect(quantityErrorMessage).toBeInTheDocument()
    })

    it('should display error message on pre-submit error', async () => {
      // Given
      await renderStockItem(props, store)
      const modifyButton = screen.getByAltText('Modifier le stock').closest('button')
      fireEvent.click(modifyButton)

      const priceInput = await screen.findByDisplayValue('10')
      const quantityInput = await screen.findByDisplayValue('20')

      // When
      fireEvent.change(priceInput, { target: { value: -10 } })
      fireEvent.change(quantityInput, { target: { value: -20 } })
      const submitIcon = await screen.findByAltText('Valider les modifications')
      const submitButton = submitIcon.closest('button')
      fireEvent.click(submitButton)

      // Then
      const errorMessage = await screen.findByText('Impossible de modifier le stock.', {
        exact: false,
      })
      expect(errorMessage).toBeInTheDocument()
      const priceErrorMessage = await screen.findByText('Le prix doit être positif.', {
        exact: false,
      })
      expect(priceErrorMessage).toBeInTheDocument()
      const quantityErrorMessage = await screen.findByText('Le stock doit être positif.', {
        exact: false,
      })
      expect(quantityErrorMessage).toBeInTheDocument()
      const quantityToLowErrorMessage = await screen.findByText(
        'La quantité ne peut être inférieure au nombre de réservations.',
        {
          exact: false,
        }
      )
      expect(quantityToLowErrorMessage).toBeInTheDocument()
    })

    it('should display success message on success', async () => {
      // Given
      pcapi.updateStock.mockImplementation(() => Promise.resolve())

      await renderStockItem(props, store)
      const modifyButton = screen.getByAltText('Modifier le stock').closest('button')
      fireEvent.click(modifyButton)
      const submitIcon = await screen.findByAltText('Valider les modifications')
      const submitButton = submitIcon.closest('button')
      // When
      fireEvent.click(submitButton)

      // Then
      const errorMessage = await screen.findByText('Le stock a bien été modifié.', { exact: false })
      expect(errorMessage).toBeInTheDocument()
    })
  })
})
