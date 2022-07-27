import '@testing-library/jest-dom'

import { fireEvent, render, screen, waitFor } from '@testing-library/react'
import React from 'react'
import { Provider } from 'react-redux'
import { MemoryRouter } from 'react-router'

import * as pcapi from 'repository/pcapi/pcapi'
import { configureTestStore } from 'store/testUtils'

import Offerers from '../Offerers'

const renderOfferers = async (props, store) => {
  render(
    <Provider store={store}>
      <MemoryRouter>
        <Offerers {...props} />
      </MemoryRouter>
    </Provider>
  )
}

jest.mock('repository/pcapi/pcapi', () => ({
  getOfferers: jest.fn(),
}))

describe('src | components | Offerers', () => {
  let props
  let offerer
  let store

  beforeEach(() => {
    offerer = { id: 'AE', siren: '1234567' }
    props = {
      closeNotification: jest.fn(),
      currentUser: {},
      isOffererCreationAvailable: true,
      location: {
        search: '',
      },
      query: {
        parse: () => ({ 'mots-cles': null }),
      },
      showNotification: jest.fn(),
    }
    store = configureTestStore({
      user: { currentUser: { publicName: 'François', isAdmin: false } },
    })
    pcapi.getOfferers.mockResolvedValue({
      offerers: [offerer],
      nbTotalResults: 1,
    })
  })

  describe('render', () => {
    describe('subtitle message', () => {
      describe('when the isOffererCreationAvailable feature is activated', () => {
        it('should display a link to create an offer', async () => {
          // when
          renderOfferers(props, store)

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
        it('should display a link to create an offer', async () => {
          // given
          props.isOffererCreationAvailable = false

          // when
          renderOfferers(props, store)

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
        renderOfferers(props, store)

        // then
        await waitFor(() =>
          expect(screen.getByText('Structure juridique')).toBeInTheDocument()
        )
      })

      it('should display Structures juridiques when many offerers', async () => {
        // given
        pcapi.getOfferers.mockResolvedValue({
          offerers: [{ id: 'AE' }, { id: 'AF' }],
          nbTotalResults: 2,
        })

        // when
        renderOfferers(props, store)

        // then
        await waitFor(() =>
          expect(screen.getByText('Structures juridiques')).toBeInTheDocument()
        )
      })
    })

    describe('when leaving page', () => {
      it('should not close notifcation', async () => {
        // given
        props = { ...props, closeNotification: jest.fn() }
        renderOfferers(props, store)

        // when
        fireEvent.click(
          screen.getByText('créer un nouveau lieu', { selector: 'a' })
        )

        // then
        await waitFor(() =>
          expect(props.closeNotification).not.toHaveBeenCalled()
        )
      })

      it('should not fail on null notifcation', async () => {
        // given
        props = {
          ...props,
          closeNotification: jest.fn(),
          notification: null,
        }
        renderOfferers(props, store)

        // when
        fireEvent.click(
          screen.getByText('créer un nouveau lieu', { selector: 'a' })
        )

        // then
        await waitFor(() =>
          expect(props.closeNotification).not.toHaveBeenCalled()
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
          pcapi.getOfferers.mockResolvedValue({
            offerers: [offerer],
            nbTotalResults: 1,
          })

          // when
          renderOfferers(props, store)

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
            pcapi.getOfferers.mockResolvedValue({
              offerers: [offerer],
              nbTotalResults: 1,
            })

            // when
            renderOfferers(props, store)

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
            pcapi.getOfferers.mockResolvedValue({
              offerers: [offerer],
              nbTotalResults: 1,
            })

            // when
            renderOfferers(props, store)

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
          renderOfferers(props, store)

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
          props.isOffererCreationAvailable = false

          // when
          renderOfferers(props, store)

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
