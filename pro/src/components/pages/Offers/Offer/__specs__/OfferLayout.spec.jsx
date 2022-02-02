/*
 * @debt rtl "Gaël: this file contains eslint error(s) based on eslint-testing-library plugin"
 * @debt rtl "Gaël: bad use of act in testing library"
 */

import { fireEvent } from '@testing-library/dom'
import '@testing-library/jest-dom'
import {
  act,
  render,
  screen,
  waitForElementToBeRemoved,
} from '@testing-library/react'
import React from 'react'
import { Provider } from 'react-redux'
import { MemoryRouter } from 'react-router'

import NotificationContainer from 'components/layout/Notification/NotificationContainer'
import * as pcapi from 'repository/pcapi/pcapi'
import { configureTestStore } from 'store/testUtils'

import OfferLayout from '../OfferLayout'

jest.mock('repository/pcapi/pcapi', () => ({
  loadOffer: jest.fn(),
  updateOffersActiveStatus: jest.fn(),
}))

const renderOfferDetails = async (props, store) => {
  await act(async () => {
    await render(
      <Provider store={store}>
        <MemoryRouter>
          <>
            <OfferLayout {...props} />
            <NotificationContainer />
          </>
        </MemoryRouter>
      </Provider>
    )
  })
}

describe('offerLayout', () => {
  let editedOffer
  let props
  let store

  beforeEach(() => {
    store = configureTestStore({
      data: { users: [{ publicName: 'François', isAdmin: false }] },
    })
    props = {}
  })

  describe('render when editing an existing offer', () => {
    beforeEach(() => {
      editedOffer = {
        id: 'AB',
        name: 'My edited offer',
        status: 'SOLD_OUT',
      }
      props = {
        match: {
          url: '/offre/AB',
          params: { offerId: 'AB' },
        },
        location: {
          pathname: '/offre/AB/individuel/edition',
        },
      }
      pcapi.loadOffer.mockResolvedValue(editedOffer)
    })

    it('should have title "Éditer une offre"', async () => {
      // When
      await renderOfferDetails(props, store)

      // Then
      const title = await screen.findByText('Éditer une offre', {
        selector: 'h1',
      })
      expect(title).toBeInTheDocument()
    })

    it('should allow to activate inactive offer', async () => {
      // Given
      pcapi.updateOffersActiveStatus.mockResolvedValue()
      pcapi.loadOffer
        .mockResolvedValueOnce({
          ...editedOffer,
          isActive: false,
          status: 'INACTIVE',
        })
        .mockResolvedValue({ ...editedOffer, isActive: true, status: 'ACTIVE' })
      await renderOfferDetails(props, store)

      // When
      fireEvent.click(screen.getByRole('button', { name: 'Activer' }))

      // Then
      expect(pcapi.updateOffersActiveStatus).toHaveBeenCalledWith(false, {
        ids: [editedOffer.id],
        isActive: true,
      })
      await waitForElementToBeRemoved(() =>
        screen.getByRole('button', { name: 'Activer' })
      )
      expect(
        screen.getByText('L’offre a bien été activée.')
      ).toBeInTheDocument()
      expect(
        screen.getByRole('button', { name: 'Désactiver' })
      ).toBeInTheDocument()
    })

    it('should allow to deactivate active offer', async () => {
      // Given
      pcapi.updateOffersActiveStatus.mockResolvedValue()
      pcapi.loadOffer
        .mockResolvedValueOnce({
          ...editedOffer,
          isActive: true,
          status: 'ACTIVE',
        })
        .mockResolvedValue({
          ...editedOffer,
          isActive: false,
          status: 'INACTIVE',
        })
      await renderOfferDetails(props, store)

      // When
      fireEvent.click(screen.getByRole('button', { name: 'Désactiver' }))

      // Then
      expect(pcapi.updateOffersActiveStatus).toHaveBeenCalledWith(false, {
        ids: [editedOffer.id],
        isActive: false,
      })
      await waitForElementToBeRemoved(() =>
        screen.getByRole('button', { name: 'Désactiver' })
      )
      expect(
        screen.getByText('L’offre a bien été désactivée.')
      ).toBeInTheDocument()
      expect(
        screen.getByRole('button', { name: 'Activer' })
      ).toBeInTheDocument()
    })

    it('should not allow to deactivate pending offer', async () => {
      // Given
      pcapi.loadOffer.mockResolvedValue({
        ...editedOffer,
        status: 'PENDING',
        isActive: true,
      })

      // When
      await renderOfferDetails(props, store)

      // Then
      expect(screen.getByRole('button', { name: 'Désactiver' })).toBeDisabled()
    })

    it('should not allow to deactivate rejected offer', async () => {
      // Given
      pcapi.loadOffer.mockResolvedValue({
        ...editedOffer,
        status: 'REJECTED',
        isActive: false,
      })

      // When
      await renderOfferDetails(props, store)

      // Then
      expect(screen.getByRole('button', { name: 'Désactiver' })).toBeDisabled()
    })

    it('should inform user something went wrong when impossible to toggle offer status', async () => {
      // Given
      pcapi.loadOffer.mockResolvedValue({ ...editedOffer, isActive: true })
      pcapi.updateOffersActiveStatus.mockRejectedValue()
      await renderOfferDetails(props, store)

      // When
      fireEvent.click(screen.getByRole('button', { name: 'Désactiver' }))

      // Then
      await expect(
        screen.findByText(
          'Une erreur est survenue, veuillez réessayer ultérieurement.'
        )
      ).resolves.toBeInTheDocument()
      expect(
        screen.getByRole('button', { name: 'Désactiver' })
      ).toBeInTheDocument()
      expect(
        screen.queryByRole('button', { name: 'Activer' })
      ).not.toBeInTheDocument()
    })
  })

  describe('render when creating a new offer', () => {
    beforeEach(() => {
      props = {
        match: {
          url: '/offres',
          params: {},
        },
        location: {
          pathname: '/offre/AB/creation',
        },
      }
    })

    it('should have title "Ajouter une offre"', async () => {
      // When
      await renderOfferDetails(props, store)

      // Then
      expect(
        screen.getByText('Nouvelle offre', { selector: 'h1' })
      ).toBeInTheDocument()
    })
  })
})
