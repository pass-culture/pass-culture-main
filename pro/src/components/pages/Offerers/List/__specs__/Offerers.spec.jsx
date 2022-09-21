import '@testing-library/jest-dom'

import { render, screen, waitFor } from '@testing-library/react'
import React from 'react'
import { Provider } from 'react-redux'
import { MemoryRouter } from 'react-router'

import { api } from 'apiClient/api'
import { configureTestStore } from 'store/testUtils'

import Offerers from '../Offerers'

const renderOfferers = async (storeOverride = {}) => {
  const store = configureTestStore(storeOverride)
  render(
    <Provider store={store}>
      <MemoryRouter>
        <Offerers />
      </MemoryRouter>
    </Provider>
  )
}

jest.mock('apiClient/api', () => ({
  api: { getOfferers: jest.fn() },
}))

describe('src | components | Offerers', () => {
  let offerer

  beforeEach(() => {
    offerer = { id: 'AE', siren: '1234567' }
    api.getOfferers.mockResolvedValue({
      offerers: [offerer],
      nbTotalResults: 1,
    })
  })

  describe('render', () => {
    describe('subtitle message', () => {
      describe('when the isOffererCreationAvailable feature is activated', () => {
        it('should display a link to create an venue', async () => {
          // when
          renderOfferers({
            features: {
              list: [{ isActive: true, nameKey: 'API_SIRENE_AVAILABLE' }],
            },
          })

          // then
          await waitFor(() =>
            expect(screen.getByText('créer un nouveau lieu')).toHaveAttribute(
              'href',
              '/structures/AE/lieux/creation'
            )
          )
        })
      })

      describe('when the isOffererCreationAvailable feature is disabled', () => {
        it('should display a link to indisponible page', async () => {
          // when
          renderOfferers()

          // then
          await waitFor(() =>
            expect(screen.getByText('créer un nouveau lieu')).toHaveAttribute(
              'href',
              '/erreur/indisponible'
            )
          )
        })
      })
    })

    describe('should pluralize offerers menu link', () => {
      it('should display Structure juridique when one offerer', async () => {
        // when
        renderOfferers()

        // then
        await waitFor(() =>
          expect(screen.getByText('Structure juridique')).toBeInTheDocument()
        )
      })

      it('should display Structures juridiques when many offerers', async () => {
        // given
        api.getOfferers.mockResolvedValue({
          offerers: [{ id: 'AE' }, { id: 'AF' }],
          nbTotalResults: 2,
        })

        // when
        renderOfferers()

        // then
        await waitFor(() =>
          expect(screen.getByText('Structures juridiques')).toBeInTheDocument()
        )
      })
    })

    describe('when displaying the list of offerers', () => {
      describe('when the offerer is active and the user has access to it', () => {
        it('should render an active offerer item in the list for each activated offerer', async () => {
          // given
          const offerer = {
            id: 'B2',
            isValidated: true,
            userHasAccess: true,
            name: 'My Offerer',
            managedVenues: [],
          }
          api.getOfferers.mockResolvedValue({
            offerers: [offerer],
            nbTotalResults: 1,
          })

          // when
          renderOfferers()

          // then
          await waitFor(() =>
            expect(screen.getByText('My Offerer')).toBeInTheDocument()
          )
        })
      })

      describe('when offerer is not active for the user', () => {
        describe('when the offerer is not active', () => {
          it('should render a pending offerer item', async () => {
            // given
            const offerer = {
              id: 'B2',
              siren: '1431',
              isValidated: false,
              userHasAccess: true,
            }
            api.getOfferers.mockResolvedValue({
              offerers: [offerer],
              nbTotalResults: 1,
            })

            // when
            renderOfferers()

            // then
            await waitFor(() =>
              expect(
                screen.getByText('Rattachement en cours de validation')
              ).toBeInTheDocument()
            )
          })
        })

        describe('when the user does not have access', () => {
          it('should render a pending offerer item', async () => {
            // given
            const offerer = {
              id: 'B2',
              siren: '1431',
              isValidated: true,
              userHasAccess: false,
            }
            api.getOfferers.mockResolvedValue({
              offerers: [offerer],
              nbTotalResults: 1,
            })

            // when
            renderOfferers()

            // then
            await waitFor(() =>
              expect(
                screen.getByText('Rattachement en cours de validation')
              ).toBeInTheDocument()
            )
          })
        })
      })
    })

    describe('the link to offerer creation page', () => {
      describe('when api sirene feature is available', () => {
        it('should display a link to create an offer', async () => {
          // when
          renderOfferers({
            features: {
              list: [{ isActive: true, nameKey: 'API_SIRENE_AVAILABLE' }],
            },
          })

          // then
          await waitFor(() =>
            expect(screen.getByText('Ajouter une structure')).toHaveAttribute(
              'href',
              '/structures/creation'
            )
          )
        })
      })

      describe('when api sirene feature is not available', () => {
        it('should display a link to unavailable page', async () => {
          // given

          // when
          renderOfferers()

          // then
          await waitFor(() =>
            expect(screen.getByText('Ajouter une structure')).toHaveAttribute(
              'href',
              '/erreur/indisponible'
            )
          )
        })
      })
    })
  })
})
