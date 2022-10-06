import '@testing-library/jest-dom'

import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import React from 'react'
import { Provider } from 'react-redux'
import { MemoryRouter, Route } from 'react-router'

import { api } from 'apiClient/api'
import Notification from 'components/layout/Notification/Notification'
import OfferLayout from 'components/pages/Offers/Offer/OfferLayout'
import * as pcapi from 'repository/pcapi/pcapi'
import { configureTestStore } from 'store/testUtils'
import { offerFactory, stockFactory } from 'utils/apiFactories'
import { getToday } from 'utils/date'
import { loadFakeApiStocks } from 'utils/fakeApi'
import { queryByTextTrimHtml } from 'utils/testHelpers'

const GUYANA_CAYENNE_DEPT = '973'
const PARIS_FRANCE_DEPT = '75'

jest.mock('repository/pcapi/pcapi', () => ({
  deleteStock: jest.fn(),
}))

jest.mock('apiClient/api', () => ({
  api: {
    getCategories: jest.fn(),
    getOffer: jest.fn(),
    listOfferersNames: jest.fn(),
    getVenues: jest.fn(),
    getStocks: jest.fn(),
    upsertStocks: jest.fn(),
  },
}))

jest.mock('utils/date', () => ({
  ...jest.requireActual('utils/date'),
  getToday: jest
    .fn()
    .mockImplementation(() => new Date('2020-12-15T12:00:00Z')),
}))

const renderOffers = (
  props,
  storeOverrides,
  pathname = '/offre/AG3A/individuel/stocks'
) => {
  const store = configureTestStore(storeOverrides)
  render(
    <Provider store={store}>
      <MemoryRouter initialEntries={[{ pathname: pathname }]}>
        <Route path="/offre/:offerId([A-Z0-9]+)/individuel">
          {() => <OfferLayout {...props} />}
        </Route>
      </MemoryRouter>
      <Notification />
    </Provider>
  )
}

describe('stocks page', () => {
  let props
  let defaultOffer
  let defaultStock
  let stockId
  let store
  beforeEach(() => {
    store = {
      user: {
        currentUser: { publicName: 'François', isAdmin: false },
        initialized: true,
      },
      features: {
        initialized: true,
        list: [],
      },
    }
    props = {}

    defaultOffer = {
      ...offerFactory(),
      id: 'AG3A',
      venue: {
        id: 'BC',
        departementCode: GUYANA_CAYENNE_DEPT,
        managingOfferer: {
          id: 'AB',
          name: 'offerer name',
        },
      },
      isEvent: false,
      status: 'ACTIVE',
      stocks: [],
    }

    stockId = '2E'
    defaultStock = {
      activationCodes: [],
      activationCodesExpirationDatetime: null,
      quantity: 10,
      price: 10.01,
      remainingQuantity: 6,
      bookingsQuantity: 4,
      bookingLimitDatetime: '2020-12-18T23:59:59Z',
      id: stockId,
      isEventDeletable: true,
    }
    jest.spyOn(api, 'getOffer').mockResolvedValue(defaultOffer)
    api.getStocks.mockResolvedValue({ stocks: [] })
    api.getCategories.mockResolvedValue({
      categories: [],
      subcategories: [],
    })
    pcapi.deleteStock.mockResolvedValue({ id: stockId })
    api.upsertStocks.mockResolvedValue({})
    jest.spyOn(api, 'listOfferersNames').mockResolvedValue({
      offerersNames: [
        {
          id: 'AB',
          name: 'offerer name',
        },
      ],
    })
    jest.spyOn(api, 'getVenues').mockResolvedValue({
      venues: [
        {
          id: 'BC',
          isVirtual: false,
          managingOffererId: 'AB',
          name: 'venue name',
          offererName: 'offerer name',
        },
      ],
    })
  })

  describe('edit', () => {
    it('should update displayed offer status', async () => {
      // Given
      const initialOffer = {
        ...defaultOffer,
        status: 'ACTIVE',
      }
      const updatedOffer = {
        ...defaultOffer,
        status: 'SOLD_OUT',
      }
      jest
        .spyOn(api, 'getOffer')
        .mockResolvedValueOnce(initialOffer)
        .mockResolvedValueOnce(updatedOffer)
      api.getStocks
        .mockResolvedValueOnce({ stocks: [defaultStock] })
        .mockResolvedValueOnce({ stocks: [] })

      // When
      renderOffers(props, store)

      // Then
      expect(await screen.findByText('publiée')).toBeInTheDocument()

      // When

      await userEvent.click(screen.getByTitle('Supprimer le stock'))
      await userEvent.click(
        await screen.findByText('Supprimer', { selector: 'button' })
      )

      // Then
      expect(screen.queryByText('épuisée')).toBeInTheDocument()
    })

    it('should go on recap page after validating of stocks', async () => {
      // Given
      const stock = stockFactory()
      loadFakeApiStocks([stock])
      renderOffers(props, store)

      // When
      await userEvent.click(
        await screen.findByText('Enregistrer les modifications', {
          selector: 'button',
        })
      )

      // Then
      expect(
        screen.getByText('Récapitulatif', {
          selector: 'h1',
        })
      ).toBeInTheDocument()
    })

    describe('event offer', () => {
      let eventOffer
      beforeEach(() => {
        const eventStock = {
          ...defaultStock,
          beginningDatetime: '2020-12-20T22:00:00Z',
        }
        eventOffer = {
          ...defaultOffer,
          isEvent: true,
        }

        jest.spyOn(api, 'getOffer').mockResolvedValue(eventOffer)
        api.getStocks.mockResolvedValue({ stocks: [eventStock] })
      })

      describe('when offer has been manually created', () => {
        it('should not be able to edit a stock when expired', async () => {
          // Given
          const dayAfterBeginningDatetime = new Date('2020-12-21T12:00:00Z')
          getToday.mockImplementationOnce(() => dayAfterBeginningDatetime)

          // When
          renderOffers(props, store)

          // Then
          expect(await screen.findByLabelText('Prix')).toBeDisabled()
          expect(screen.getByLabelText('Date de l’évènement')).toBeDisabled()
          expect(screen.getByLabelText('Heure de l’évènement')).toBeDisabled()
          expect(
            screen.getByLabelText('Date limite de réservation')
          ).toBeDisabled()
          expect(screen.getByLabelText('Quantité')).toBeDisabled()
        })

        it('should not be able to delete a non deletable stock', async () => {
          // Given
          const eventOffer = {
            ...defaultOffer,
            isEvent: true,
            stocks: [
              {
                ...defaultStock,
                beginningDatetime: '2020-12-20T22:00:00Z',
                isEventDeletable: false,
              },
            ],
          }

          jest.spyOn(api, 'getOffer').mockResolvedValue(eventOffer)
          renderOffers(props, store)

          // When
          await userEvent.click(await screen.findByTitle('Supprimer le stock'))

          // Then
          expect(screen.getByTitle('Supprimer le stock')).toHaveAttribute(
            'aria-disabled',
            'true'
          )
          expect(pcapi.deleteStock).not.toHaveBeenCalled()
        })

        it('should inform user that stock cannot be updated when event is over', async () => {
          // When
          const eventInThePast = {
            ...defaultStock,
            beginningDatetime: '2020-12-14T22:00:00Z',
            isEventDeletable: true,
            isEventEditable: false,
          }

          api.getStocks.mockResolvedValue({ stocks: [eventInThePast] })
          renderOffers(props, store)

          // Then
          expect(
            await screen.findByRole('row', {
              name: 'Les évènements passés ne sont pas modifiables',
            })
          ).toBeInTheDocument()
        })

        it('should inform user that stock cannot be updated when event is over when beginningDatetime is with milliseconds', async () => {
          // When
          const eventInThePast = {
            ...defaultStock,
            beginningDatetime: '2020-12-09T20:15:00.231Z',
            isEventDeletable: true,
            isEventEditable: false,
          }

          api.getStocks.mockResolvedValue({ stocks: [eventInThePast] })
          renderOffers(props, store)

          // Then
          expect(
            await screen.findByRole('row', {
              name: 'Les évènements passés ne sont pas modifiables',
            })
          ).toBeInTheDocument()
        })

        it('should inform user that stock cannot be deleted when event is over for more than 48h', async () => {
          // When
          const eventInThePast = {
            ...defaultStock,
            beginningDatetime: '2020-12-20T22:00:00Z',
            isEventDeletable: false,
          }

          api.getStocks.mockResolvedValue({ stocks: [eventInThePast] })
          renderOffers(props, store)

          // Then
          expect(
            await screen.findByTitle(
              'Les évènements terminés depuis plus de 48h ne peuvent être supprimés'
            )
          ).toBeInTheDocument()
        })

        describe('when editing stock', () => {
          it('should be able to edit beginning date field', async () => {
            // given
            renderOffers(props, store)

            // when
            await userEvent.click(await screen.findByDisplayValue('20/12/2020'))
            await userEvent.click(screen.getByText('21'))

            // then
            expect(
              screen.queryByDisplayValue('20/12/2020')
            ).not.toBeInTheDocument()
            expect(screen.getByDisplayValue('21/12/2020')).toBeInTheDocument()
          })

          it('should not be able to select beginning date before today', async () => {
            // given
            renderOffers(props, store)

            // when
            await userEvent.click(await screen.findByDisplayValue('20/12/2020'))
            await userEvent.click(screen.getByText('13'))

            // then
            expect(
              screen.queryByDisplayValue('13/12/2020')
            ).not.toBeInTheDocument()
            expect(screen.getByDisplayValue('20/12/2020')).toBeInTheDocument()
          })

          it('should be able to remove date field', async () => {
            // given
            renderOffers(props, store)

            // when
            await userEvent.clear(
              await screen.findByLabelText('Date de l’évènement')
            )

            // then
            expect(screen.getByLabelText('Date de l’évènement')).toBeEnabled()
          })

          it('should be able to edit hour field', async () => {
            // given
            renderOffers(props, store)

            // when
            await userEvent.click(await screen.findByDisplayValue('19:00'))
            await userEvent.click(screen.getByText('18:30'))

            // then
            expect(screen.queryByDisplayValue('19:00')).not.toBeInTheDocument()
            expect(screen.getByDisplayValue('18:30')).toBeInTheDocument()
          })

          it('should be able to edit price field', async () => {
            // given
            renderOffers(props, store)
            const priceField = await screen.findByDisplayValue('10.01')

            // when
            await userEvent.clear(priceField)
            await userEvent.type(priceField, '127.03')

            // then
            expect(screen.queryByDisplayValue('10.01')).not.toBeInTheDocument()
            expect(screen.getByDisplayValue('127.03')).toBeInTheDocument()
          })

          it('should be able to edit booking limit date field', async () => {
            // given
            renderOffers(props, store)

            // when
            await userEvent.click(await screen.findByDisplayValue('18/12/2020'))
            await userEvent.click(screen.getByText('17'))

            // then
            expect(
              screen.queryByDisplayValue('18/12/2020')
            ).not.toBeInTheDocument()
            expect(screen.getByDisplayValue('17/12/2020')).toBeInTheDocument()
          })

          it('should not be able to select booking limit date after beginning date', async () => {
            // given
            renderOffers(props, store)

            // when
            await userEvent.click(await screen.findByDisplayValue('18/12/2020'))
            await userEvent.click(screen.getByText('21'))

            // then
            expect(
              screen.queryByDisplayValue('21/12/2020')
            ).not.toBeInTheDocument()
            expect(screen.getByDisplayValue('18/12/2020')).toBeInTheDocument()
          })

          it('should set booking limit datetime to beginning datetime when selecting a beginning datetime prior to booking limit datetime', async () => {
            // given
            renderOffers(props, store)

            // when
            await userEvent.click(await screen.findByDisplayValue('20/12/2020'))
            await userEvent.click(screen.getByText('17'))

            // then
            expect(
              screen.getByLabelText('Date limite de réservation').value
            ).toBe('17/12/2020')
          })

          it('should be able to edit total quantity field', async () => {
            // given
            renderOffers(props, store)
            const quantityField = await screen.findByDisplayValue('10')

            // when
            await userEvent.clear(quantityField)
            await userEvent.type(quantityField, '23')

            // then
            expect(screen.queryByDisplayValue('10')).not.toBeInTheDocument()
            expect(screen.getByDisplayValue('23')).toBeInTheDocument()
          })

          it('should not empty date field when emptying hour field', async () => {
            // given
            renderOffers(props, store)

            // when
            await userEvent.clear(await screen.findByDisplayValue('19:00'))

            // then
            expect(screen.queryByDisplayValue('20/12/2020')).toBeInTheDocument()
          })

          it('should compute remaining quantity based on inputted total quantity', async () => {
            // given
            renderOffers(props, store)
            const quantityField = await screen.findByDisplayValue('10')

            // when
            await userEvent.clear(quantityField)
            await userEvent.type(quantityField, '9')

            // then
            const initialRemainingQuantity = screen.queryByText(6)
            expect(initialRemainingQuantity).not.toBeInTheDocument()

            const computedRemainingQuantity = screen.queryByText('5')
            expect(computedRemainingQuantity).toBeInTheDocument()
          })

          it('should set remaining quantity to Illimité when emptying total quantity field', async () => {
            // given
            renderOffers(props, store)

            // when
            await userEvent.clear(await screen.findByDisplayValue('10'))

            // then
            const computedRemainingQuantity = screen.getByText('Illimité')
            expect(computedRemainingQuantity).toBeInTheDocument()
          })

          it('should not set remaining quantity to Illimité when total quantity is zero', async () => {
            // given
            api.getStocks.mockResolvedValue({
              stocks: [
                {
                  ...defaultStock,
                  beginningDatetime: '2020-12-20T22:00:00Z',
                  quantity: 0,
                  bookingsQuantity: 0,
                },
              ],
            })

            // when
            renderOffers(props, store)

            // then
            expect(await screen.findByLabelText('Quantité')).toHaveValue(0)
            const remainingQuantityValue =
              screen.getAllByRole('cell')[5].textContent
            expect(remainingQuantityValue).not.toBe('Illimité')
            expect(remainingQuantityValue).toBe('0')
          })

          describe('when clicking on submit button', () => {
            beforeEach(() => {
              api.upsertStocks.mockResolvedValue({})
            })

            it('should update stock', async () => {
              // Given
              renderOffers(props, store)

              await userEvent.click(
                await screen.findByLabelText('Date de l’évènement')
              )
              await userEvent.click(screen.getByText('26'))

              await userEvent.click(
                screen.getByLabelText('Heure de l’évènement')
              )
              await userEvent.click(screen.getByText('20:00'))

              const priceField = screen.getByLabelText('Prix')
              await userEvent.clear(priceField)
              await userEvent.type(priceField, '14.01')

              await userEvent.click(
                screen.getByLabelText('Date limite de réservation')
              )
              await userEvent.click(screen.getByText('25'))

              const quantityField = screen.getByLabelText('Quantité')
              await userEvent.clear(quantityField)
              await userEvent.type(quantityField, '6')

              // When
              await userEvent.click(
                screen.getByText('Enregistrer les modifications')
              )

              // Then
              expect(api.upsertStocks).toHaveBeenCalledWith({
                offerId: defaultOffer.id,
                stocks: [
                  {
                    beginningDatetime: '2020-12-26T23:00:00Z',
                    bookingLimitDatetime: '2020-12-26T02:59:59Z',
                    id: '2E',
                    price: '14.01',
                    quantity: '6',
                  },
                ],
              })
            })

            it('should refresh stocks', async () => {
              // Given
              const stock = {
                ...defaultStock,
                beginningDatetime: '2020-12-20T22:00:00Z',
              }
              const initialStock = {
                ...stock,
                price: 10.01,
              }
              const updatedStock = {
                ...stock,
                price: 10,
              }
              api.getStocks
                .mockResolvedValueOnce({ stocks: [initialStock] })
                .mockResolvedValueOnce({ stocks: [updatedStock] })
              renderOffers(props, store)

              // When
              await userEvent.click(
                await screen.findByText('Enregistrer les modifications')
              )

              // Then
              expect(api.getStocks).toHaveBeenCalledTimes(2)
            })

            it('should set booking limit datetime to exact beginning datetime when not specified', async () => {
              // Given
              renderOffers(props, store)
              await userEvent.clear(
                await screen.findByLabelText('Date limite de réservation')
              )

              // When
              await userEvent.click(
                screen.getByText('Enregistrer les modifications')
              )

              // Then
              const savedStocks = api.upsertStocks.mock.calls[0][0].stocks
              expect(savedStocks[0].bookingLimitDatetime).toBe(
                '2020-12-20T22:00:00Z'
              )
            })

            it('should set booking limit datetime to exact beginning datetime when same as beginning date', async () => {
              // Given
              renderOffers(props, store)
              await userEvent.click(
                await screen.findByLabelText('Date limite de réservation')
              )
              await userEvent.click(screen.getByText('20'))

              // When
              await userEvent.click(
                screen.getByText('Enregistrer les modifications')
              )

              // Then
              const savedStocks = api.upsertStocks.mock.calls[0][0].stocks
              expect(savedStocks[0].bookingLimitDatetime).toBe(
                '2020-12-20T22:00:00Z'
              )
            })

            it('should set booking limit time to end of selected locale day when specified and different than beginning date in Cayenne TZ', async () => {
              // Given
              renderOffers(props, store)
              await userEvent.click(
                await screen.findByLabelText('Date limite de réservation')
              )
              await userEvent.click(screen.getByText('19'))

              // When
              await userEvent.click(
                screen.getByText('Enregistrer les modifications')
              )

              // Then
              const savedStocks = api.upsertStocks.mock.calls[0][0].stocks
              expect(savedStocks[0].bookingLimitDatetime).toBe(
                '2020-12-20T02:59:59Z'
              )
            })

            it('should set booking limit time to end of selected locale day when specified and different than beginning date in Paris TZ', async () => {
              // Given
              eventOffer.venue.departementCode = PARIS_FRANCE_DEPT

              renderOffers(props, store)
              await userEvent.click(
                await screen.findByLabelText('Date limite de réservation')
              )
              await userEvent.click(screen.getByText('17'))

              // When
              await userEvent.click(
                screen.getByText('Enregistrer les modifications')
              )

              // Then
              const savedStocks = api.upsertStocks.mock.calls[0][0].stocks
              expect(savedStocks[0].bookingLimitDatetime).toBe(
                '2020-12-17T22:59:59Z'
              )
            })

            it('should set quantity to null when not specified', async () => {
              // Given
              renderOffers(props, store)
              await userEvent.clear(await screen.findByLabelText('Quantité'))

              // When
              await userEvent.click(
                screen.getByText('Enregistrer les modifications')
              )

              // Then
              const savedStocks = api.upsertStocks.mock.calls[0][0].stocks
              expect(savedStocks[0].quantity).toBeNull()
            })

            it('should display error message on api error', async () => {
              // Given
              api.upsertStocks.mockRejectedValueOnce({
                errors: {
                  price: 'Le prix est invalide.',
                  quantity: 'La quantité est invalide.',
                },
              })
              renderOffers(props, store)

              await userEvent.click(
                await screen.findByLabelText('Date de l’évènement')
              )
              await userEvent.click(screen.getByText('26'))

              await userEvent.click(
                screen.getByLabelText('Heure de l’évènement')
              )
              await userEvent.click(screen.getByText('20:00'))

              // When
              await userEvent.click(
                screen.getByText('Enregistrer les modifications')
              )

              // Then
              const errorMessage = await screen.findByText(
                'Une ou plusieurs erreurs sont présentes dans le formulaire.'
              )
              expect(errorMessage).toBeInTheDocument()
            })

            it('should not be able to submit changes when beginning date field is empty', async () => {
              // given
              renderOffers(props, store)
              const beginningDateField = await screen.findByDisplayValue(
                '20/12/2020'
              )
              await userEvent.clear(beginningDateField)

              // when
              await userEvent.click(
                screen.getByText('Enregistrer les modifications')
              )

              // then
              const errorMessage = await screen.findByText(
                'Une ou plusieurs erreurs sont présentes dans le formulaire.'
              )
              expect(errorMessage).toBeInTheDocument()
              expect(api.upsertStocks).not.toHaveBeenCalled()
            })

            it('should not be able to validate changes when hour field is empty', async () => {
              // given
              renderOffers(props, store)
              const beginningHourField = await screen.findByDisplayValue(
                '19:00'
              )
              await userEvent.clear(beginningHourField)

              // when
              await userEvent.click(
                screen.getByText('Enregistrer les modifications')
              )

              // then
              const errorMessage = await screen.findByText(
                'Une ou plusieurs erreurs sont présentes dans le formulaire.'
              )
              expect(errorMessage).toBeInTheDocument()
              expect(api.upsertStocks).not.toHaveBeenCalled()
            })

            it('should not display price error when the price is above 300 euros and offer is not educational', async () => {
              // Given
              renderOffers(props, store)
              await userEvent.type(await screen.findByLabelText('Prix'), '301')

              // When
              await userEvent.click(
                screen.getByText('Enregistrer les modifications')
              )

              // Then
              expect(
                queryByTextTrimHtml(
                  screen,
                  'Le prix d’une offre ne peut excéder 300 euros. Pour plus d’infos, merci de consulter nos Conditions Générales d’Utilisation'
                )
              ).not.toBeInTheDocument()

              expect(
                screen.queryByText(
                  'Une ou plusieurs erreurs sont présentes dans le formulaire.'
                )
              ).not.toBeInTheDocument()
            })

            it('should be able to edit stock when remaining quantity is unlimited and there is existing bookings', async () => {
              // Given
              const eventStock = {
                ...defaultStock,
                beginningDatetime: '2020-12-20T22:00:00Z',
                quantity: null,
              }
              api.getStocks.mockResolvedValue({ stocks: [eventStock] })
              api.upsertStocks.mockResolvedValue({})

              renderOffers(props, store)
              await userEvent.click(
                await screen.findByLabelText('Heure de l’évènement')
              )
              await userEvent.click(screen.getByText('20:00'))

              // When
              await userEvent.click(
                screen.getByText('Enregistrer les modifications')
              )

              // Then
              const errorMessage = await screen.findByText(
                'Vos modifications ont bien été enregistrées'
              )
              expect(errorMessage).toBeInTheDocument()
            })

            it('should display error message on pre-submit error', async () => {
              // Given
              renderOffers(props, store)

              await userEvent.click(
                await screen.findByLabelText('Date de l’évènement')
              )
              await userEvent.click(screen.getByText('26'))

              await userEvent.click(
                screen.getByLabelText('Heure de l’évènement')
              )
              await userEvent.click(screen.getByText('20:00'))

              await userEvent.type(screen.getByLabelText('Prix'), '-10')
              await userEvent.type(screen.getByLabelText('Quantité'), '-20')

              // When
              await userEvent.click(
                screen.getByText('Enregistrer les modifications')
              )

              // Then
              const errorMessage = await screen.findByText(
                'Une ou plusieurs erreurs sont présentes dans le formulaire.'
              )
              expect(errorMessage).toBeInTheDocument()
            })

            it('should display success message on success', async () => {
              // Given
              api.upsertStocks.mockResolvedValue({})
              renderOffers(props, store)

              await userEvent.click(
                await screen.findByLabelText('Date de l’évènement')
              )
              await userEvent.click(screen.getByText('26'))

              await userEvent.click(
                screen.getByLabelText('Heure de l’évènement')
              )
              await userEvent.click(screen.getByText('20:00'))

              // When
              await userEvent.click(
                screen.getByText('Enregistrer les modifications')
              )

              // Then
              const errorMessage = await screen.findByText(
                'Vos modifications ont bien été enregistrées'
              )
              expect(errorMessage).toBeInTheDocument()
            })

            it('should refresh offer', async () => {
              // Given
              api.upsertStocks.mockResolvedValue({})
              const initialOffer = {
                ...eventOffer,
                status: 'SOLD_OUT',
              }
              const updatedOffer = {
                ...eventOffer,
                status: 'ACTIVE',
              }
              jest
                .spyOn(api, 'getOffer')
                .mockResolvedValueOnce(initialOffer)
                .mockResolvedValueOnce(updatedOffer)
              renderOffers(props, store)
              api.getOffer.mockClear()

              // When
              await userEvent.click(
                await screen.findByText('Enregistrer les modifications')
              )

              // Then
              expect(api.getOffer).toHaveBeenCalledTimes(2)
            })

            it('should update displayed offer status', async () => {
              // Given
              api.upsertStocks.mockResolvedValue({})
              const initialOffer = {
                ...eventOffer,
                status: 'SOLD_OUT',
              }
              const updatedOffer = {
                ...eventOffer,
                status: 'ACTIVE',
              }
              jest
                .spyOn(api, 'getOffer')
                .mockResolvedValueOnce(initialOffer)
                .mockResolvedValueOnce(updatedOffer)

              // When
              renderOffers(props, store)

              // Then
              const soldOutOfferStatus = await screen.findByText('épuisée')
              expect(soldOutOfferStatus).toBeInTheDocument()

              await userEvent.click(
                screen.getByText('Enregistrer les modifications')
              )

              const successMessage = await screen.findByText(
                'Vos modifications ont bien été enregistrées'
              )
              expect(successMessage).toBeInTheDocument()

              const activeOfferStatus = await screen.findByText('publiée')
              expect(activeOfferStatus).toBeInTheDocument()
            })
          })
        })

        describe('when deleting stock', () => {
          it('should display confirmation dialog box with focus on confirmation button', async () => {
            // Given
            renderOffers(props, store)

            // When
            await userEvent.click(
              await screen.findByTitle('Supprimer le stock')
            )

            // Then
            expect(
              screen.getByText('Voulez-vous supprimer ce stock ?')
            ).toBeInTheDocument()
            expect(
              queryByTextTrimHtml(
                screen,
                'Ce stock ne sera plus disponible à la réservation et entraînera l’annulation des réservations en cours et validées !'
              )
            ).toBeInTheDocument()
            expect(
              screen.getByText(
                'entraînera l’annulation des réservations en cours et validées !',
                {
                  selector: 'strong',
                }
              )
            ).toBeInTheDocument()
            expect(
              screen.getByText(
                'L’ensemble des utilisateurs concernés sera automatiquement averti par e-mail.'
              )
            ).toBeInTheDocument()
          })

          it('should be able to delete a stock', async () => {
            // Given
            renderOffers(props, store)

            // When
            await userEvent.click(
              await screen.findByTitle('Supprimer le stock')
            )
            await userEvent.click(
              screen.getByRole('button', { name: 'Supprimer' })
            )

            // Then
            expect(pcapi.deleteStock).toHaveBeenCalledWith(stockId)
          })

          it('should not delete stock if aborting on confirmation', async () => {
            // Given
            renderOffers(props, store)

            // When
            await userEvent.click(
              await screen.findByTitle('Supprimer le stock')
            )
            await userEvent.click(
              screen.getByRole('button', { name: 'Annuler' })
            )

            // Then
            expect(pcapi.deleteStock).not.toHaveBeenCalled()
          })

          it('should discard deleted stock from list', async () => {
            // Given
            const initialStock = {
              ...defaultStock,
              beginningDatetime: '2020-12-20T22:00:00Z',
            }
            api.getStocks
              .mockResolvedValueOnce({ stocks: [initialStock] })
              .mockResolvedValueOnce({ stocks: [] })

            renderOffers(props, store)

            // When
            await userEvent.click(
              await screen.findByTitle('Supprimer le stock')
            )
            await userEvent.click(
              screen.getByRole('button', { name: 'Supprimer' })
            )

            // Then
            expect(screen.queryByRole('row')).not.toBeInTheDocument()
          })

          it('should not discard creation stocks when deleting a stock', async () => {
            // Given
            const initialStock = {
              ...defaultStock,
              beginningDatetime: '2020-12-20T22:00:00Z',
            }
            api.getStocks
              .mockResolvedValueOnce({ stocks: [initialStock] })
              .mockResolvedValueOnce({ stocks: [] })
            jest.spyOn(api, 'getOffer').mockResolvedValue({
              ...defaultOffer,
              isEvent: true,
            })

            renderOffers(props, store)
            await userEvent.click(await screen.findByText('Ajouter une date'))

            let nbExpectedRows = 0
            nbExpectedRows += 1 // header row
            nbExpectedRows += 1 // existing stock row
            nbExpectedRows += 1 // creation stock row
            expect(screen.getAllByRole('row')).toHaveLength(nbExpectedRows)

            // When
            await userEvent.click(
              screen.getAllByTitle('Opérations sur le stock')[0]
            )
            await userEvent.click(screen.getAllByText('Supprimer le stock')[0])
            await userEvent.click(
              await screen.findByRole('button', { name: 'Supprimer' })
            )

            // Then
            expect(
              screen.queryByTestId(`stock-item-${initialStock.id}`)
            ).not.toBeInTheDocument()
            nbExpectedRows = 0
            nbExpectedRows += 1 // header row
            nbExpectedRows += 1 // creation stock row
            expect(screen.getAllByRole('row')).toHaveLength(nbExpectedRows)
          })

          it('should display a success message after deletion', async () => {
            // Given
            renderOffers(props, store)

            // When
            await userEvent.click(
              await screen.findByTitle('Supprimer le stock')
            )
            await userEvent.click(
              screen.getByRole('button', { name: 'Supprimer' })
            )

            // Then
            await expect(
              screen.findByText('Le stock a été supprimé.')
            ).resolves.toBeInTheDocument()
          })

          it('should display an error message when deletion fails', async () => {
            // Given
            pcapi.deleteStock.mockRejectedValue({})
            renderOffers(props, store)

            // When
            await userEvent.click(
              await screen.findByTitle('Supprimer le stock')
            )
            await userEvent.click(
              screen.getByRole('button', { name: 'Supprimer' })
            )

            // Then
            await expect(
              screen.findByText(
                'Une erreur est survenue lors de la suppression du stock.'
              )
            ).resolves.toBeInTheDocument()
          })

          it('should disable deleting button', async () => {
            // given
            renderOffers(props, store)

            // when
            const deleteButton = await screen.findByTitle('Supprimer le stock')
            await userEvent.click(deleteButton)

            // then
            expect(deleteButton).toHaveAttribute('aria-disabled', 'true')
          })
        })
      })

      describe('when offer has been synchronized with Allocine', () => {
        beforeEach(() => {
          const eventOfferFromAllocine = {
            ...eventOffer,
            lastProvider: {
              id: 'CY',
              name: 'allociné',
            },
          }

          jest.spyOn(api, 'getOffer').mockResolvedValue(eventOfferFromAllocine)
        })

        describe('when editing stock', () => {
          it('should be able to update price and quantity but not beginning date nor hour fields', async () => {
            // When
            renderOffers(props, store)

            // Then
            expect(
              await screen.findByLabelText('Date de l’évènement')
            ).toBeDisabled()
            expect(screen.getByLabelText('Heure de l’évènement')).toBeDisabled()
            expect(
              screen.getByLabelText('Date limite de réservation')
            ).toBeEnabled()
            expect(screen.getByLabelText('Prix')).toBeEnabled()
            expect(screen.getByLabelText('Quantité')).toBeEnabled()
          })
        })
      })
    })

    describe('thing offer', () => {
      let thingOffer
      beforeEach(() => {
        const thingStock = {
          ...defaultStock,
          isEventDeletable: true,
        }
        thingOffer = {
          ...defaultOffer,
          isEvent: false,
        }
        jest.spyOn(api, 'getOffer').mockResolvedValue(thingOffer)
        api.getStocks.mockResolvedValue({ stocks: [thingStock] })
      })

      describe('when offer has been manually created', () => {
        it('should be able to edit price field', async () => {
          // given
          renderOffers(props, store)
          const priceField = await screen.findByDisplayValue('10.01')

          // when
          await userEvent.clear(priceField)
          await userEvent.type(priceField, '127.03')

          // then
          expect(screen.queryByDisplayValue('10.01')).not.toBeInTheDocument()
          expect(screen.getByDisplayValue('127.03')).toBeInTheDocument()
        })

        it('should be able to edit booking limit date field', async () => {
          // given
          renderOffers(props, store)

          // when
          await userEvent.click(await screen.findByDisplayValue('18/12/2020'))
          await userEvent.click(screen.getByText('17'))

          // then
          expect(
            screen.queryByDisplayValue('18/12/2020')
          ).not.toBeInTheDocument()
          expect(screen.getByDisplayValue('17/12/2020')).toBeInTheDocument()
        })

        it('should be able to edit total quantity field', async () => {
          // given
          renderOffers(props, store)
          const quantityField = await screen.findByDisplayValue('10')

          // when
          await userEvent.clear(quantityField)
          await userEvent.type(quantityField, '23')

          // then
          expect(screen.queryByDisplayValue('10')).not.toBeInTheDocument()
          expect(screen.getByDisplayValue('23')).toBeInTheDocument()
        })

        it('should compute remaining quantity based on inputted total quantity', async () => {
          // given
          renderOffers(props, store)
          const quantityField = await screen.findByDisplayValue('10')

          // when
          await userEvent.clear(quantityField)
          await userEvent.type(quantityField, '9')

          // then
          const initialRemainingQuantity = screen.queryByText(6)
          expect(initialRemainingQuantity).not.toBeInTheDocument()

          const computedRemainingQuantity = screen.queryByText('5')
          expect(computedRemainingQuantity).toBeInTheDocument()
        })

        it('should set remaining quantity to Illimité when emptying total quantity field', async () => {
          // given
          renderOffers(props, store)

          // when
          await userEvent.clear(await screen.findByDisplayValue('10'))

          // then
          const computedRemainingQuantity = screen.getByText('Illimité')
          expect(computedRemainingQuantity).toBeInTheDocument()
        })

        it('should not set remaining quantity to Illimité when total quantity is zero', async () => {
          // given
          api.getStocks.mockResolvedValue({
            stocks: [{ ...defaultStock, quantity: 0, bookingsQuantity: 0 }],
          })

          // when
          renderOffers(props, store)

          // then
          expect(await screen.findByLabelText('Quantité')).toHaveValue(0)
          const remainingQuantityValue =
            screen.getAllByRole('cell')[3].textContent
          expect(remainingQuantityValue).toBe('0')
        })

        describe('when clicking on submit button', () => {
          it('should save changes done to stock', async () => {
            // Given
            api.upsertStocks.mockResolvedValue({})
            renderOffers(props, store)

            const priceField = await screen.findByLabelText('Prix')
            await userEvent.clear(priceField)
            await userEvent.type(priceField, '14.01')

            await userEvent.click(
              screen.getByLabelText('Date limite de réservation')
            )
            await userEvent.click(screen.getByText('25'))

            const quantityField = screen.getByLabelText('Quantité')
            await userEvent.clear(quantityField)
            await userEvent.type(quantityField, '6')

            // When
            await userEvent.click(
              screen.getByText('Enregistrer les modifications')
            )

            // Then
            expect(api.upsertStocks).toHaveBeenCalledWith({
              offerId: defaultOffer.id,
              stocks: [
                {
                  bookingLimitDatetime: '2020-12-26T02:59:59Z',
                  id: '2E',
                  price: '14.01',
                  quantity: '6',
                },
              ],
            })
          })

          it('should refresh stocks', async () => {
            // Given
            api.upsertStocks.mockResolvedValue({})
            const initialStock = {
              ...defaultStock,
              price: 10.01,
            }
            const updatedStock = {
              ...defaultStock,
              price: 10,
            }
            api.getStocks
              .mockResolvedValueOnce({ stocks: [initialStock] })
              .mockResolvedValueOnce({ stocks: [updatedStock] })
            renderOffers(props, store)

            // When
            await userEvent.click(
              await screen.findByText('Enregistrer les modifications')
            )

            // Then
            expect(api.getStocks).toHaveBeenCalledTimes(2)
          })

          it('should set booking limit time to end of selected local day when specified in Cayenne TZ', async () => {
            // Given
            api.upsertStocks.mockResolvedValue({})
            renderOffers(props, store)
            await userEvent.click(
              await screen.findByLabelText('Date limite de réservation')
            )
            await userEvent.click(screen.getByText('19'))

            // When
            await userEvent.click(
              screen.getByText('Enregistrer les modifications')
            )

            // Then
            const savedStocks = api.upsertStocks.mock.calls[0][0].stocks
            expect(savedStocks[0].bookingLimitDatetime).toBe(
              '2020-12-20T02:59:59Z'
            )
          })

          it('should set booking limit time to end of selected local day when specified in Paris TZ', async () => {
            // Given
            thingOffer.venue.departementCode = PARIS_FRANCE_DEPT

            api.upsertStocks.mockResolvedValue({})
            renderOffers(props, store)
            await userEvent.click(
              await screen.findByLabelText('Date limite de réservation')
            )
            await userEvent.click(screen.getByText('17'))

            // When
            await userEvent.click(
              screen.getByText('Enregistrer les modifications')
            )

            // Then
            const savedStocks = api.upsertStocks.mock.calls[0][0].stocks
            expect(savedStocks[0].bookingLimitDatetime).toBe(
              '2020-12-17T22:59:59Z'
            )
          })

          it('should set booking limit datetime to null when not specified', async () => {
            // Given
            api.upsertStocks.mockResolvedValue({})
            renderOffers(props, store)

            await userEvent.clear(
              await screen.findByLabelText('Date limite de réservation')
            )

            // When
            await userEvent.click(
              screen.getByText('Enregistrer les modifications')
            )

            // Then
            const savedStocks = api.upsertStocks.mock.calls[0][0].stocks
            expect(savedStocks[0].bookingLimitDatetime).toBeNull()
          })

          it('should set quantity to null when not specified', async () => {
            // Given
            api.upsertStocks.mockResolvedValue({})
            renderOffers(props, store)
            await userEvent.clear(await screen.findByLabelText('Quantité'))

            // When
            await userEvent.click(
              screen.getByText('Enregistrer les modifications')
            )
            // Then
            const savedStocks = api.upsertStocks.mock.calls[0][0].stocks
            expect(savedStocks[0].quantity).toBeNull()
          })

          it('should display price error when the price is above 300 euros and offer is not educational', async () => {
            // Given
            renderOffers(props, store)
            await userEvent.clear(await screen.findByLabelText('Prix'))
            await userEvent.type(await screen.findByLabelText('Prix'), '301')

            // When
            await userEvent.click(
              screen.getByText('Enregistrer les modifications')
            )

            // Then
            expect(
              queryByTextTrimHtml(
                screen,
                'Le prix d’une offre ne peut excéder 300 euros. Pour plus d’infos, merci de consulter nos Conditions Générales d’Utilisation'
              )
            ).toBeInTheDocument()
          })

          it('should display error message on api error', async () => {
            // Given
            api.upsertStocks.mockRejectedValueOnce({
              errors: {
                price: 'Le prix est invalide.',
                quantity: 'La quantité est invalide.',
              },
            })
            renderOffers(props, store)

            await userEvent.type(await screen.findByLabelText('Quantité'), '10')

            // When
            await userEvent.click(
              screen.getByText('Enregistrer les modifications')
            )

            // Then
            const errorMessage = await screen.findByText(
              'Une ou plusieurs erreurs sont présentes dans le formulaire.'
            )
            expect(errorMessage).toBeInTheDocument()
          })

          it('should display error message on pre-submit error', async () => {
            // Given
            renderOffers(props, store)

            await userEvent.type(await screen.findByLabelText('Prix'), '-10')
            await userEvent.type(screen.getByLabelText('Quantité'), '-20')

            // When
            await userEvent.click(
              screen.getByText('Enregistrer les modifications')
            )

            // Then
            const errorMessage = await screen.findByText(
              'Une ou plusieurs erreurs sont présentes dans le formulaire.'
            )
            expect(errorMessage).toBeInTheDocument()
          })

          it('should display success message on success', async () => {
            // Given
            api.upsertStocks.mockResolvedValue({})
            renderOffers(props, store)

            await userEvent.type(await screen.findByLabelText('Quantité'), '10')

            // When
            await userEvent.click(
              screen.getByText('Enregistrer les modifications')
            )

            // Then
            const errorMessage = await screen.findByText(
              'Vos modifications ont bien été enregistrées'
            )
            expect(errorMessage).toBeInTheDocument()
          })
        })
      })

      describe('when offer has been synchronized (with Titelive, leslibraires.fr, FNAC or Praxiel)', () => {
        beforeEach(() => {
          const synchronisedThingOffer = {
            ...thingOffer,
            lastProvider: {
              id: 'D4',
              name: 'fnac',
            },
          }
          jest.spyOn(api, 'getOffer').mockResolvedValue(synchronisedThingOffer)
        })

        it('should not be able to edit a stock', async () => {
          // When
          renderOffers(props, store)

          // Then
          expect(await screen.findByLabelText('Prix')).toBeDisabled()
          expect(
            screen.getByLabelText('Date limite de réservation')
          ).toBeDisabled()
          expect(screen.getByLabelText('Quantité')).toBeDisabled()
        })

        it('should not be able to delete a stock', async () => {
          // Given
          renderOffers(props, store)
          const deleteButton = await screen.findByTitle(
            'Les stock synchronisés ne peuvent être supprimés'
          )

          // When
          await userEvent.click(deleteButton)

          // Then
          expect(deleteButton).toHaveAttribute('aria-disabled', 'true')
          expect(screen.getAllByRole('row')).toHaveLength(2)
        })
      })

      describe('digital offer', () => {
        it('should disable add activation codes option', async () => {
          // when
          jest
            .spyOn(api, 'getOffer')
            .mockResolvedValue({ ...thingOffer, isDigital: true })
          renderOffers(props, store)

          // then
          const informationMessage = await screen.findByText(
            'Ajouter des codes d’activation'
          )
          expect(informationMessage.parentElement).toHaveAttribute(
            'aria-disabled',
            'true'
          )
        })
      })

      it('should warn that pending booking will be canceled on thing offer stock deletion', async () => {
        // Given
        renderOffers(props, store)

        // When
        await userEvent.click(await screen.findByTitle('Supprimer le stock'))

        // Then
        expect(
          queryByTextTrimHtml(
            screen,
            'Ce stock ne sera plus disponible à la réservation et entraînera l’annulation des réservations en cours !'
          )
        ).toBeInTheDocument()
        expect(
          screen.getByText(
            'entraînera l’annulation des réservations en cours !',
            {
              selector: 'strong',
            }
          )
        ).toBeInTheDocument()
      })
    })
  })
})
