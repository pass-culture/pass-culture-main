import '@testing-library/jest-dom'
import { act, fireEvent, render, screen, within } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import React from 'react'
import { Provider } from 'react-redux'
import { MemoryRouter, Route } from 'react-router'

import NotificationContainer from 'components/layout/Notification/NotificationContainer'
import OfferLayoutContainer from 'components/pages/Offers/Offer/OfferLayoutContainer'
import * as pcapi from 'repository/pcapi/pcapi'
import { configureTestStore } from 'store/testUtils'
import { getToday } from 'utils/date'
import { queryByTextTrimHtml } from 'utils/testHelpers'

jest.mock('repository/pcapi/pcapi', () => ({
  deleteStock: jest.fn(),
  loadOffer: jest.fn(),
  loadStocks: jest.fn(),
  bulkCreateOrEditStock: jest.fn(),
}))

jest.mock('utils/date', () => ({
  ...jest.requireActual('utils/date'),
  getToday: jest.fn().mockImplementation(() => new Date('2020-12-15T12:00:00Z')),
}))

const renderOffers = async (props, store) => {
  await act(async () => {
    await render(
      <Provider store={store}>
        <MemoryRouter initialEntries={[{ pathname: '/offres/AG3A/stocks' }]}>
          <Route path="/offres/:offerId([A-Z0-9]+)/">
            <>
              <OfferLayoutContainer {...props} />
              <NotificationContainer />
            </>
          </Route>
        </MemoryRouter>
      </Provider>
    )
  })
}

describe('stocks page', () => {
  let props
  let defaultOffer
  let defaultStock
  let stockId
  let store
  beforeEach(() => {
    store = configureTestStore({ data: { users: [{ publicName: 'François', isAdmin: false }] } })
    props = {}

    defaultOffer = {
      id: 'AG3A',
      venue: {
        departementCode: '973',
      },
      isEvent: false,
      stocks: [],
    }

    stockId = '2E'
    defaultStock = {
      quantity: 10,
      price: 10.01,
      remainingQuantity: 6,
      bookingsQuantity: 4,
      bookingLimitDatetime: '2020-12-18T23:59:59Z',
      id: stockId,
      isEventDeletable: true,
    }
    pcapi.loadOffer.mockResolvedValue(defaultOffer)
    pcapi.loadStocks.mockResolvedValue({ stocks: [] })
    pcapi.deleteStock.mockResolvedValue({ id: stockId })
  })

  describe('render', () => {
    describe('when no stocks yet', () => {
      it('should not display empty stock list', async () => {
        // given
        pcapi.loadStocks.mockResolvedValue({ stocks: [] })

        // when
        await renderOffers(props, store)

        // then
        expect(await screen.queryByRole('table')).not.toBeInTheDocument()
      })

      it('should not display action buttons', async () => {
        // given
        pcapi.loadStocks.mockResolvedValue({ stocks: [] })

        // when
        await renderOffers(props, store)

        // then
        expect(await screen.queryByText('Annuler et quitter')).not.toBeInTheDocument()
        expect(await screen.queryByText('Enregistrer')).not.toBeInTheDocument()
      })

      it('should display add stock button', async () => {
        // given
        pcapi.loadStocks.mockResolvedValue({ stocks: [] })

        // when
        await renderOffers(props, store)

        // then
        expect(await screen.findByText('Ajouter un stock')).toBeInTheDocument()
      })
    })

    it('should load stocks on mount', async () => {
      // when
      await renderOffers(props, store)

      // then
      expect(pcapi.loadStocks).toHaveBeenCalledTimes(1)
    })

    it('should display "Gratuit" when stock is free', async () => {
      // given
      const freeStock = {
        stocks: [
          {
            ...defaultStock,
            price: 0,
          },
        ],
      }

      pcapi.loadStocks.mockResolvedValue(freeStock)

      // when
      await renderOffers(props, store)

      // then
      expect((await screen.findByPlaceholderText('Gratuit')).value).toBe('')
    })

    it('should display stocks sorted by descending beginning datetime', async () => {
      // given
      const offerWithMultipleStocks = {
        ...defaultOffer,
        isEvent: true,
      }
      const stocks = [
        {
          ...defaultStock,
          beginningDatetime: '2020-12-20T22:00:00Z',
        },
        {
          ...defaultStock,
          id: '3F',
          beginningDatetime: '2020-12-25T20:00:00Z',
        },
        {
          ...defaultStock,
          id: '4G',
          beginningDatetime: '2020-12-20T20:00:00Z',
        },
      ]
      pcapi.loadOffer.mockResolvedValue(offerWithMultipleStocks)
      pcapi.loadStocks.mockResolvedValue({ stocks })

      // when
      await renderOffers(props, store)

      // then
      const beginningDatetimeFields = await screen.findAllByLabelText('Date de l’événement')
      const hourFields = await screen.findAllByLabelText('Heure de l’événement')
      expect(beginningDatetimeFields[0].value).toBe('25/12/2020')
      expect(beginningDatetimeFields[1].value).toBe('20/12/2020')
      expect(hourFields[1].value).toBe('19:00')
      expect(beginningDatetimeFields[1].value).toBe('20/12/2020')
      expect(hourFields[2].value).toBe('17:00')
    })

    it('should display "Illimité" for total quantity when stock has unlimited quantity', async () => {
      // given
      const unlimitedStock = {
        ...defaultStock,
        quantity: null,
      }

      pcapi.loadStocks.mockResolvedValue({ stocks: [unlimitedStock] })

      // when
      await renderOffers(props, store)

      // then
      expect((await screen.findByPlaceholderText('Illimité')).value).toBe('')
    })

    it('should display "Illimité" for remaining quantity when stock has unlimited quantity', async () => {
      // given
      const unlimitedStock = {
        ...defaultStock,
        quantity: null,
      }
      pcapi.loadStocks.mockResolvedValue({ stocks: [unlimitedStock] })

      // when
      await renderOffers(props, store)

      // then
      expect(await screen.findByText('Illimité')).toBeInTheDocument()
    })

    it('should have cancel link to go back to offer details', async () => {
      // given
      const offer = {
        ...defaultOffer,
        stocks: [],
      }

      pcapi.loadOffer.mockResolvedValue(offer)
      pcapi.loadStocks.mockResolvedValue({
        stocks: [
          {
            ...defaultStock,
            quantity: 10,
          },
        ],
      })

      // when
      await renderOffers(props, store)

      // then
      const cancelLink = screen.getByRole('link', { name: 'Annuler et quitter' })
      expect(cancelLink).toBeInTheDocument()
      expect(cancelLink).toHaveAttribute('href', '/offres/AG3A/edition')
    })

    describe('when fraud detection', () => {
      let offer = {}
      let stocks = {}

      beforeEach(() => {
        offer = {
          ...defaultOffer,
          isEvent: true,
          stocks: [],
        }
        stocks = {
          stocks: [
            {
              ...defaultStock,
              beginningDatetime: '2222-12-20T22:00:00Z',
              quantity: 10,
            },
          ],
        }
      })

      it('should display status informative message and disable all fields when offer is rejected', async () => {
        // given
        offer.status = 'REJECTED'
        offer.isActive = false
        pcapi.loadOffer.mockResolvedValue(offer)
        pcapi.loadStocks.mockResolvedValue(stocks)

        // when
        await renderOffers(props, store)

        // then
        expect(
          screen.getByText(
            'Votre offre a été refusée car elle ne respecte pas les Conditions Générales d’Utilisation du pass. Un e-mail contenant les conditions d’éligibilité d’une offre a été envoyé à l’adresse e-mail attachée à votre compte.'
          )
        ).toBeInTheDocument()
        expect(screen.getByText('Ajouter une date')).toBeDisabled()
        expect(screen.getByLabelText('Date de l’événement')).toBeDisabled()
        expect(screen.getByLabelText('Heure de l’événement')).toBeDisabled()
        expect(screen.getByLabelText('Prix')).toBeDisabled()
        expect(screen.getByLabelText('Date limite de réservation')).toBeDisabled()
        expect(screen.getByLabelText('Quantité')).toBeDisabled()
        expect(screen.getByTitle('Supprimer le stock')).toBeDisabled()
        expect(screen.getByText('Enregistrer')).toBeDisabled()
      })

      it('should display status informative message and disable all fields when offer is awaiting for validation', async () => {
        // given
        offer.status = 'AWAITING'
        offer.isActive = true
        pcapi.loadOffer.mockResolvedValue(offer)
        pcapi.loadStocks.mockResolvedValue(stocks)

        // when
        await renderOffers({}, store)

        // then
        expect(
          screen.getByText(
            'Votre offre est en cours de validation par l’équipe du pass Culture. Une fois validée, vous recevrez un e-mail de confirmation et votre offre sera automatiquement mise en ligne.'
          )
        ).toBeInTheDocument()
        expect(screen.getByText('Ajouter une date')).toBeDisabled()
        expect(screen.getByLabelText('Date de l’événement')).toBeDisabled()
        expect(screen.getByLabelText('Heure de l’événement')).toBeDisabled()
        expect(screen.getByLabelText('Prix')).toBeDisabled()
        expect(screen.getByLabelText('Date limite de réservation')).toBeDisabled()
        expect(screen.getByLabelText('Quantité')).toBeDisabled()
        expect(screen.getByTitle('Supprimer le stock')).toBeDisabled()
        expect(screen.getByText('Enregistrer')).toBeDisabled()
      })
    })

    describe('render event offer', () => {
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

        pcapi.loadOffer.mockResolvedValue(eventOffer)
        pcapi.loadStocks.mockResolvedValue({ stocks: [eventStock] })
      })

      it('should display an information message regarding booking cancellation', async () => {
        // when
        await renderOffers(props, store)

        // then
        const informationMessage = screen.getByText(
          'Les utilisateurs ont un délai de 48h pour annuler leur réservation mais ne peuvent pas le faire moins de 48h avant le début de l’événement. Si la date limite de réservation n’est pas encore passée, la place est alors automatiquement remise en vente.'
        )
        expect(informationMessage).toBeInTheDocument()
      })

      it('should display button to add date', async () => {
        // when
        await renderOffers(props, store)

        // then
        const buttonAddDate = await screen.findByRole('button', { name: 'Ajouter une date' })
        expect(buttonAddDate).toBeInTheDocument()
      })

      it("should display offer's stocks fields", async () => {
        // when
        await renderOffers(props, store)

        // then
        expect(pcapi.loadOffer).toHaveBeenCalledWith('AG3A')

        const columnHeaders = await screen.findAllByRole('columnheader')
        const columnCells = await screen.findAllByRole('cell')

        expect(columnHeaders).toHaveLength(8)

        expect(columnHeaders[0].textContent).toBe('Date')
        expect(columnCells[0].querySelector('input').value).toBe('20/12/2020')

        expect(columnHeaders[1].textContent).toBe('Horaire')
        expect(columnCells[1].querySelector('input').value).toBe('19:00')

        expect(columnHeaders[2].textContent).toBe('Prix')
        expect(columnCells[2].querySelector('input').value).toBe('10.01')

        expect(columnHeaders[3].textContent).toBe('Date limite de réservation')
        expect(columnCells[3].querySelector('input').value).toBe('18/12/2020')

        expect(columnHeaders[4].textContent).toBe('Quantité')
        expect(columnCells[4].querySelector('input').value).toBe('10')

        expect(columnHeaders[5].textContent).toBe('Stock restant')
        expect(columnCells[5].textContent).toBe('6')

        expect(columnHeaders[6].textContent).toBe('Réservations')
        expect(columnCells[6].textContent).toBe('4')

        expect(columnCells[7].querySelector('[alt="Supprimer le stock"]')).toBeInTheDocument()
      })
    })

    describe('render thing offer', () => {
      let thingOffer
      beforeEach(() => {
        thingOffer = {
          ...defaultOffer,
          isEvent: false,
        }
        pcapi.loadOffer.mockResolvedValue(thingOffer)
        pcapi.loadStocks.mockResolvedValue({ stocks: [{ ...defaultStock }] })
      })

      it('should display an information message regarding booking cancellation', async () => {
        // when
        await renderOffers(props, store)

        // then
        const informationMessage = screen.getByText(
          'Les utilisateurs ont 30 jours pour faire valider leur contremarque. Passé ce délai, la réservation est automatiquement annulée et l’offre remise en vente.'
        )
        expect(informationMessage).toBeInTheDocument()
      })

      it('should display button to add stock', async () => {
        // given
        pcapi.loadStocks.mockResolvedValue({ stocks: [] })

        // when
        await renderOffers(props, store)

        // then
        expect(screen.getByRole('button', { name: 'Ajouter un stock' })).toBeEnabled()
      })

      it('should not be able to add a new stock if there is already one', async () => {
        // When
        await renderOffers(props, store)

        // Then
        expect(screen.queryByRole('button', { name: 'Ajouter un stock' })).not.toBeInTheDocument()
      })

      it("should display offer's stock fields", async () => {
        // when
        await renderOffers(props, store)

        // then
        expect(pcapi.loadOffer).toHaveBeenCalledWith('AG3A')

        const columnHeaders = await screen.findAllByRole('columnheader')
        const columnCells = await screen.findAllByRole('cell')

        expect(columnHeaders).toHaveLength(6)

        expect(columnHeaders[0].textContent).toBe('Prix')
        expect(columnCells[0].querySelector('input').value).toBe('10.01')

        expect(columnHeaders[1].textContent).toBe('Date limite de réservation')
        expect(columnCells[1].querySelector('input').value).toBe('18/12/2020')

        expect(columnHeaders[2].textContent).toBe('Quantité')
        expect(columnCells[2].querySelector('input').value).toBe('10')

        expect(columnHeaders[3].textContent).toBe('Stock restant')
        expect(columnCells[3].textContent).toBe('6')

        expect(columnHeaders[4].textContent).toBe('Réservations')
        expect(columnCells[4].textContent).toBe('4')

        expect(columnCells[5].querySelector('[alt="Supprimer le stock"]')).toBeInTheDocument()
      })

      describe('when offer is synchronized', () => {
        beforeEach(() => {
          const synchronisedThingOffer = {
            ...defaultOffer,
            isEvent: false,
            lastProvider: {
              id: 'D4',
              name: 'fnac',
            },
          }
          pcapi.loadOffer.mockResolvedValue(synchronisedThingOffer)
          pcapi.loadStocks.mockResolvedValue({ stocks: [] })
        })

        it('should not be able to add a stock', async () => {
          // Given
          pcapi.loadStocks.mockResolvedValue({
            stocks: [
              {
                ...defaultStock,
                quantity: 10,
              },
            ],
          })

          // When
          await renderOffers(props, store)

          // Then
          expect(screen.queryByRole('button', { name: 'Ajouter un stock' })).not.toBeInTheDocument()
        })
      })
    })

    describe('render digital offer', () => {
      let digitalOffer
      beforeEach(() => {
        digitalOffer = {
          ...defaultOffer,
          isDigital: true,
          isEvent: false,
        }
        pcapi.loadOffer.mockResolvedValue(digitalOffer)
        pcapi.loadStocks.mockResolvedValue({ stocks: [{ ...defaultStock }] })
      })

      it('should display an information message regarding booking cancellation (new rules)', async () => {
        store = configureTestStore({
          data: {
            users: [{ publicName: 'François', isAdmin: false }],
            features: [{ isActive: true, nameKey: 'AUTO_ACTIVATE_DIGITAL_BOOKINGS' }],
          },
        })

        // when
        await renderOffers(props, store)

        // then
        const informationMessage = screen.getByText(
          "Les utilisateurs ne peuvent pas annuler leurs réservations d'offres numériques. Toute réservation est définitive et sera immédiatement validée."
        )
        expect(informationMessage).toBeInTheDocument()
      })

      it('should display an information message regarding booking cancellation (legacy rules)', async () => {
        // when
        await renderOffers(props, store)

        // then
        const informationMessage = screen.getByText(
          'Les utilisateurs ont 30 jours pour faire valider leur contremarque. Passé ce délai, la réservation est automatiquement annulée et l’offre remise en vente.'
        )
        expect(informationMessage).toBeInTheDocument()
      })
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
      pcapi.loadOffer.mockResolvedValueOnce(initialOffer).mockResolvedValueOnce(updatedOffer)
      pcapi.loadStocks
        .mockResolvedValueOnce({ stocks: [defaultStock] })
        .mockResolvedValueOnce({ stocks: [] })

      // When
      await renderOffers(props, store)

      // Then
      expect(screen.getByText('active')).toBeInTheDocument()

      // When
      await act(async () => {
        fireEvent.click(screen.getByTitle('Supprimer le stock'))
        await fireEvent.click(await screen.findByText('Supprimer', { selector: 'button' }))
      })

      // Then
      expect(screen.queryByText('épuisée')).toBeInTheDocument()
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

        pcapi.loadOffer.mockResolvedValue(eventOffer)
        pcapi.loadStocks.mockResolvedValue({ stocks: [eventStock] })
      })

      describe('when offer has been manually created', () => {
        it('should not be able to edit a stock when expired', async () => {
          // Given
          const dayAfterBeginningDatetime = new Date('2020-12-21T12:00:00Z')
          getToday.mockImplementationOnce(() => dayAfterBeginningDatetime)

          // When
          await renderOffers(props, store)

          // Then
          expect(screen.getByLabelText('Prix')).toBeDisabled()
          expect(screen.getByLabelText('Date de l’événement')).toBeDisabled()
          expect(screen.getByLabelText('Heure de l’événement')).toBeDisabled()
          expect(screen.getByLabelText('Date limite de réservation')).toBeDisabled()
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

          pcapi.loadOffer.mockResolvedValue(eventOffer)
          await renderOffers(props, store)

          // When
          userEvent.click(screen.getByTitle('Supprimer le stock'))

          // Then
          expect(screen.getByTitle('Supprimer le stock').closest('button')).toBeDisabled()
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

          pcapi.loadStocks.mockResolvedValue({ stocks: [eventInThePast] })
          await renderOffers(props, store)

          // Then
          expect(
            screen.getByRole('row', { name: 'Les évènements passés ne sont pas modifiables' })
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

          pcapi.loadStocks.mockResolvedValue({ stocks: [eventInThePast] })
          await renderOffers(props, store)

          // Then
          expect(
            screen.getByRole('row', { name: 'Les évènements passés ne sont pas modifiables' })
          ).toBeInTheDocument()
        })

        it('should inform user that stock cannot be deleted when event is over for more than 48h', async () => {
          // When
          const eventInThePast = {
            ...defaultStock,
            beginningDatetime: '2020-12-20T22:00:00Z',
            isEventDeletable: false,
          }

          pcapi.loadStocks.mockResolvedValue({ stocks: [eventInThePast] })
          await renderOffers(props, store)

          // Then
          expect(
            screen.getByTitle(
              'Les évènements terminés depuis plus de 48h ne peuvent être supprimés'
            )
          ).toBeInTheDocument()
        })

        describe('when editing stock', () => {
          it('should be able to edit beginning date field', async () => {
            // given
            await renderOffers(props, store)

            // when
            userEvent.click(screen.getByDisplayValue('20/12/2020'))
            userEvent.click(screen.getByText('21'))

            // then
            expect(screen.queryByDisplayValue('20/12/2020')).not.toBeInTheDocument()
            expect(screen.getByDisplayValue('21/12/2020')).toBeInTheDocument()
          })

          it('should not be able to select beginning date before today', async () => {
            // given
            await renderOffers(props, store)

            // when
            userEvent.click(screen.getByDisplayValue('20/12/2020'))
            userEvent.click(screen.getByText('13'))

            // then
            expect(screen.queryByDisplayValue('13/12/2020')).not.toBeInTheDocument()
            expect(screen.getByDisplayValue('20/12/2020')).toBeInTheDocument()
          })

          it('should be able to remove date field', async () => {
            // given
            await renderOffers(props, store)

            // when
            userEvent.clear(screen.getByLabelText('Date de l’événement'))

            // then
            expect(screen.getByLabelText('Date de l’événement')).toBeEnabled()
          })

          it('should be able to edit hour field', async () => {
            // given
            await renderOffers(props, store)

            // when
            userEvent.click(screen.getByDisplayValue('19:00'))
            userEvent.click(screen.getByText('18:30'))

            // then
            expect(screen.queryByDisplayValue('19:00')).not.toBeInTheDocument()
            expect(screen.getByDisplayValue('18:30')).toBeInTheDocument()
          })

          it('should be able to edit price field', async () => {
            // given
            await renderOffers(props, store)
            const priceField = screen.getByDisplayValue('10.01')

            // when
            userEvent.clear(priceField)
            userEvent.type(priceField, '127.03')

            // then
            expect(screen.queryByDisplayValue('10.01')).not.toBeInTheDocument()
            expect(screen.getByDisplayValue('127.03')).toBeInTheDocument()
          })

          it('should be able to edit booking limit date field', async () => {
            // given
            await renderOffers(props, store)

            // when
            userEvent.click(screen.getByDisplayValue('18/12/2020'))
            userEvent.click(screen.getByText('17'))

            // then
            expect(screen.queryByDisplayValue('18/12/2020')).not.toBeInTheDocument()
            expect(screen.getByDisplayValue('17/12/2020')).toBeInTheDocument()
          })

          it('should not be able to select booking limit date after beginning date', async () => {
            // given
            await renderOffers(props, store)

            // when
            userEvent.click(screen.getByDisplayValue('18/12/2020'))
            userEvent.click(screen.getByText('21'))

            // then
            expect(screen.queryByDisplayValue('21/12/2020')).not.toBeInTheDocument()
            expect(screen.getByDisplayValue('18/12/2020')).toBeInTheDocument()
          })

          it('should set booking limit datetime to beginning datetime when selecting a beginning datetime prior to booking limit datetime', async () => {
            // given
            await renderOffers(props, store)

            // when
            userEvent.click(screen.getByDisplayValue('20/12/2020'))
            userEvent.click(screen.getByText('17'))

            // then
            expect(screen.getByLabelText('Date limite de réservation').value).toBe('17/12/2020')
          })

          it('should be able to edit total quantity field', async () => {
            // given
            await renderOffers(props, store)
            const quantityField = screen.getByDisplayValue('10')

            // when
            userEvent.clear(quantityField)
            userEvent.type(quantityField, '23')

            // then
            expect(screen.queryByDisplayValue('10')).not.toBeInTheDocument()
            expect(screen.getByDisplayValue('23')).toBeInTheDocument()
          })

          it('should not empty date field when emptying hour field', async () => {
            // given
            await renderOffers(props, store)

            // when
            userEvent.clear(screen.getByDisplayValue('19:00'))

            // then
            expect(screen.queryByDisplayValue('20/12/2020')).toBeInTheDocument()
          })

          it('should compute remaining quantity based on inputted total quantity', async () => {
            // given
            await renderOffers(props, store)
            const quantityField = screen.getByDisplayValue('10')

            // when
            userEvent.clear(quantityField)
            userEvent.type(quantityField, '9')

            // then
            const initialRemainingQuantity = screen.queryByText(6)
            expect(initialRemainingQuantity).not.toBeInTheDocument()

            const computedRemainingQuantity = screen.queryByText('5')
            expect(computedRemainingQuantity).toBeInTheDocument()
          })

          it('should set remaining quantity to Illimité when emptying total quantity field', async () => {
            // given
            await renderOffers(props, store)

            // when
            userEvent.clear(screen.getByDisplayValue('10'))

            // then
            const computedRemainingQuantity = screen.getByText('Illimité')
            expect(computedRemainingQuantity).toBeInTheDocument()
          })

          it('should not set remaining quantity to Illimité when total quantity is zero', async () => {
            // given
            pcapi.loadStocks.mockResolvedValue({
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
            await renderOffers(props, store)

            // then
            expect(screen.getByLabelText('Quantité').value).not.toBe('')
            expect(screen.getByLabelText('Quantité').value).toBe('0')
            const remainingQuantityValue = screen.getAllByRole('cell')[5].textContent
            expect(remainingQuantityValue).not.toBe('Illimité')
            expect(remainingQuantityValue).toBe('0')
          })

          describe('when clicking on submit button', () => {
            beforeEach(() => {
              pcapi.bulkCreateOrEditStock.mockResolvedValue({})
            })

            it('should save changes done to stock', async () => {
              // Given
              await renderOffers(props, store)

              userEvent.click(screen.getByLabelText('Date de l’événement'))
              userEvent.click(screen.getByText('26'))

              userEvent.click(screen.getByLabelText('Heure de l’événement'))
              userEvent.click(screen.getByText('20:00'))

              const priceField = screen.getByLabelText('Prix')
              userEvent.clear(priceField)
              userEvent.type(priceField, '14.01')

              userEvent.click(screen.getByLabelText('Date limite de réservation'))
              userEvent.click(screen.getByText('25'))

              const quantityField = screen.getByLabelText('Quantité')
              userEvent.clear(quantityField)
              userEvent.type(quantityField, '6')

              // When
              userEvent.click(screen.getByText('Enregistrer'))

              // Then
              expect(pcapi.bulkCreateOrEditStock).toHaveBeenCalledWith(defaultOffer.id, [
                {
                  beginningDatetime: '2020-12-26T23:00:00Z',
                  bookingLimitDatetime: '2020-12-26T02:59:59Z',
                  id: '2E',
                  price: '14.01',
                  quantity: '6',
                },
              ])
              expect(screen.getByLabelText('Date de l’événement').value).toBe('26/12/2020')
              expect(screen.getByLabelText('Heure de l’événement').value).toBe('20:00')
              expect(screen.getByLabelText('Prix').value).toBe('14.01')
              expect(screen.getByLabelText('Date limite de réservation').value).toBe('25/12/2020')
              expect(screen.getByLabelText('Quantité').value).toBe('6')
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
              pcapi.loadStocks
                .mockResolvedValueOnce({ stocks: [initialStock] })
                .mockResolvedValueOnce({ stocks: [updatedStock] })
              await renderOffers(props, store)
              pcapi.loadStocks.mockClear()

              // When
              await act(async () => {
                await userEvent.click(screen.getByText('Enregistrer'))
              })

              // Then
              expect(pcapi.loadStocks).toHaveBeenCalledTimes(1)
            })

            it('should set booking limit datetime to exact beginning datetime when not specified', async () => {
              // Given
              await renderOffers(props, store)
              userEvent.clear(screen.getByLabelText('Date limite de réservation'))

              // When
              await act(async () => {
                await userEvent.click(screen.getByText('Enregistrer'))
              })

              // Then
              const savedStocks = pcapi.bulkCreateOrEditStock.mock.calls[0][1]
              expect(savedStocks[0].bookingLimitDatetime).toBe('2020-12-20T22:00:00Z')
            })

            it('should set booking limit datetime to exact beginning datetime when same as beginning date', async () => {
              // Given
              await renderOffers(props, store)
              userEvent.click(screen.getByLabelText('Date limite de réservation'))
              userEvent.click(screen.getByText('20'))

              // When
              await act(async () => {
                await userEvent.click(screen.getByText('Enregistrer'))
              })

              // Then
              const savedStocks = pcapi.bulkCreateOrEditStock.mock.calls[0][1]
              expect(savedStocks[0].bookingLimitDatetime).toBe('2020-12-20T22:00:00Z')
            })

            it('should set booking limit time to end of selected locale day when specified and different than beginning date in Cayenne TZ', async () => {
              // Given
              await renderOffers(props, store)
              userEvent.click(screen.getByLabelText('Date limite de réservation'))
              userEvent.click(screen.getByText('19'))

              // When
              await act(async () => {
                await userEvent.click(screen.getByText('Enregistrer'))
              })

              // Then
              const savedStocks = pcapi.bulkCreateOrEditStock.mock.calls[0][1]
              expect(savedStocks[0].bookingLimitDatetime).toBe('2020-12-20T02:59:59Z')
            })

            it('should set booking limit time to end of selected locale day when specified and different than beginning date in Paris TZ', async () => {
              // Given
              eventOffer.venue.departementCode = '75'

              await renderOffers(props, store)
              userEvent.click(screen.getByLabelText('Date limite de réservation'))
              userEvent.click(screen.getByText('17'))

              // When
              await act(async () => {
                await userEvent.click(screen.getByText('Enregistrer'))
              })

              // Then
              const savedStocks = pcapi.bulkCreateOrEditStock.mock.calls[0][1]
              expect(savedStocks[0].bookingLimitDatetime).toBe('2020-12-17T22:59:59Z')
            })

            it('should set price to 0 when not specified', async () => {
              // Given
              await renderOffers(props, store)
              userEvent.clear(screen.getByLabelText('Prix'))

              // When
              await act(async () => {
                await userEvent.click(screen.getByText('Enregistrer'))
              })

              // Then
              const savedStocks = pcapi.bulkCreateOrEditStock.mock.calls[0][1]
              expect(savedStocks[0].price).toBe(0)
            })

            it('should set quantity to null when not specified', async () => {
              // Given
              await renderOffers(props, store)
              userEvent.clear(screen.getByLabelText('Quantité'))

              // When
              await act(async () => {
                await userEvent.click(screen.getByText('Enregistrer'))
              })

              // Then
              const savedStocks = pcapi.bulkCreateOrEditStock.mock.calls[0][1]
              expect(savedStocks[0].quantity).toBeNull()
            })

            it('should display error message on api error', async () => {
              // Given
              pcapi.bulkCreateOrEditStock.mockRejectedValueOnce({
                errors: {
                  price: 'Le prix est invalide.',
                  quantity: 'La quantité est invalide.',
                },
              })
              await renderOffers(props, store)

              userEvent.click(screen.getByLabelText('Date de l’événement'))
              userEvent.click(screen.getByText('26'))

              userEvent.click(screen.getByLabelText('Heure de l’événement'))
              userEvent.click(screen.getByText('20:00'))

              // When
              await act(async () => {
                await userEvent.click(screen.getByText('Enregistrer'))
              })

              // Then
              const errorMessage = await screen.findByText(
                'Une ou plusieurs erreurs sont présentes dans le formulaire.'
              )
              expect(errorMessage).toBeInTheDocument()
            })

            it('should not be able to submit changes when beginning date field is empty', async () => {
              // given
              await renderOffers(props, store)
              const beginningDateField = screen.getByDisplayValue('20/12/2020')
              userEvent.clear(beginningDateField)

              // when
              userEvent.click(screen.getByText('Enregistrer'))

              // then
              const errorMessage = await screen.findByText(
                'Une ou plusieurs erreurs sont présentes dans le formulaire.'
              )
              expect(errorMessage).toBeInTheDocument()
              expect(pcapi.bulkCreateOrEditStock).not.toHaveBeenCalled()
            })

            it('should not be able to validate changes when hour field is empty', async () => {
              // given
              await renderOffers(props, store)
              const beginningHourField = screen.getByDisplayValue('19:00')
              userEvent.clear(beginningHourField)

              // when
              userEvent.click(screen.getByText('Enregistrer'))

              // then
              const errorMessage = await screen.findByText(
                'Une ou plusieurs erreurs sont présentes dans le formulaire.'
              )
              expect(errorMessage).toBeInTheDocument()
              expect(pcapi.bulkCreateOrEditStock).not.toHaveBeenCalled()
            })

            it('should be able to edit stock when remaining quantity is unlimited and there is existing bookings', async () => {
              // Given
              const eventStock = {
                ...defaultStock,
                beginningDatetime: '2020-12-20T22:00:00Z',
                quantity: null,
              }
              pcapi.loadStocks.mockResolvedValue({ stocks: [eventStock] })
              pcapi.bulkCreateOrEditStock.mockResolvedValue({})

              await renderOffers(props, store)
              userEvent.click(screen.getByLabelText('Heure de l’événement'))
              userEvent.click(screen.getByText('20:00'))

              // When
              await userEvent.click(screen.getByText('Enregistrer'))

              // Then
              const errorMessage = await screen.findByText('Vos stocks ont bien été sauvegardés.')
              expect(errorMessage).toBeInTheDocument()
            })

            it('should display error message on pre-submit error', async () => {
              // Given
              await renderOffers(props, store)

              userEvent.click(screen.getByLabelText('Date de l’événement'))
              userEvent.click(screen.getByText('26'))

              userEvent.click(screen.getByLabelText('Heure de l’événement'))
              userEvent.click(screen.getByText('20:00'))

              userEvent.type(screen.getByLabelText('Prix'), '-10')
              userEvent.type(screen.getByLabelText('Quantité'), '-20')

              // When
              await userEvent.click(screen.getByText('Enregistrer'))

              // Then
              const errorMessage = await screen.findByText(
                'Une ou plusieurs erreurs sont présentes dans le formulaire.'
              )
              expect(errorMessage).toBeInTheDocument()
            })

            it('should display success message on success', async () => {
              // Given
              pcapi.bulkCreateOrEditStock.mockResolvedValue({})
              await renderOffers(props, store)

              userEvent.click(screen.getByLabelText('Date de l’événement'))
              userEvent.click(screen.getByText('26'))

              userEvent.click(screen.getByLabelText('Heure de l’événement'))
              userEvent.click(screen.getByText('20:00'))

              // When
              await userEvent.click(screen.getByText('Enregistrer'))

              // Then
              const errorMessage = await screen.findByText('Vos stocks ont bien été sauvegardés.')
              expect(errorMessage).toBeInTheDocument()
            })

            it('should refresh offer', async () => {
              // Given
              pcapi.bulkCreateOrEditStock.mockResolvedValue({})
              const initialOffer = {
                ...eventOffer,
                status: 'SOLD_OUT',
              }
              const updatedOffer = {
                ...eventOffer,
                status: 'ACTIVE',
              }
              pcapi.loadOffer
                .mockResolvedValueOnce(initialOffer)
                .mockResolvedValueOnce(updatedOffer)
              await renderOffers(props, store)
              pcapi.loadOffer.mockClear()

              // When
              await fireEvent.click(screen.getByText('Enregistrer'))

              //Then
              expect(pcapi.loadOffer).toHaveBeenCalledTimes(1)
            })

            it('should update displayed offer status', async () => {
              // Given
              pcapi.bulkCreateOrEditStock.mockResolvedValue({})
              const initialOffer = {
                ...eventOffer,
                status: 'SOLD_OUT',
              }
              const updatedOffer = {
                ...eventOffer,
                status: 'ACTIVE',
              }
              pcapi.loadOffer
                .mockResolvedValueOnce(initialOffer)
                .mockResolvedValueOnce(updatedOffer)

              // When
              await renderOffers(props, store)

              // Then
              const soldOutOfferStatus = await screen.findByText('épuisée')
              expect(soldOutOfferStatus).toBeInTheDocument()

              await fireEvent.click(screen.getByText('Enregistrer'))

              const successMessage = await screen.findByText('Vos stocks ont bien été sauvegardés.')
              expect(successMessage).toBeInTheDocument()

              const activeOfferStatus = await screen.findByText('active')
              expect(activeOfferStatus).toBeInTheDocument()
            })
          })
        })

        describe('when deleting stock', () => {
          it('should display confirmation dialog box with focus on confirmation button', async () => {
            // Given
            await renderOffers(props, store)

            // When
            userEvent.click(screen.getByTitle('Supprimer le stock'))

            // Then
            expect(screen.getByLabelText('Voulez-vous supprimer ce stock ?')).toBeInTheDocument()
            expect(
              queryByTextTrimHtml(
                screen,
                'Ce stock ne sera plus disponible à la réservation et entraînera l’annulation des réservations en cours !'
              )
            ).toBeInTheDocument()
            expect(
              screen.getByText('entraînera l’annulation des réservations en cours !', {
                selector: 'strong',
              })
            ).toBeInTheDocument()
            expect(
              screen.getByText(
                'L’ensemble des utilisateurs concernés sera automatiquement averti par e-mail.'
              )
            ).toBeInTheDocument()
            expect(screen.getByRole('button', { name: 'Supprimer' })).toHaveFocus()
          })

          it('should be able to delete a stock', async () => {
            // Given
            await renderOffers(props, store)

            // When
            userEvent.click(screen.getByTitle('Supprimer le stock'))
            userEvent.click(screen.getByRole('button', { name: 'Supprimer' }))

            // Then
            expect(pcapi.deleteStock).toHaveBeenCalledWith(stockId)
          })

          it('should not delete stock if aborting on confirmation', async () => {
            // Given
            await renderOffers(props, store)

            // When
            userEvent.click(screen.getByTitle('Supprimer le stock'))
            userEvent.click(screen.getByRole('button', { name: 'Annuler' }))

            // Then
            expect(pcapi.deleteStock).not.toHaveBeenCalled()
          })

          it('should discard deleted stock from list', async () => {
            // Given
            const initialStock = {
              ...defaultStock,
              beginningDatetime: '2020-12-20T22:00:00Z',
            }
            pcapi.loadStocks
              .mockResolvedValueOnce({ stocks: [initialStock] })
              .mockResolvedValueOnce({ stocks: [] })

            await renderOffers(props, store)

            // When
            await act(async () => {
              userEvent.click(await screen.findByTitle('Supprimer le stock'))
              await userEvent.click(screen.getByRole('button', { name: 'Supprimer' }))
            })

            // Then
            expect(screen.queryByRole('row')).not.toBeInTheDocument()
          })

          it('should not discard creation stocks when deleting a stock', async () => {
            // Given
            const initialStock = {
              ...defaultStock,
              beginningDatetime: '2020-12-20T22:00:00Z',
            }
            pcapi.loadStocks
              .mockResolvedValueOnce({ stocks: [initialStock] })
              .mockResolvedValueOnce({ stocks: [] })
            pcapi.loadOffer.mockResolvedValue({ ...defaultOffer, isEvent: true })

            await renderOffers(props, store)
            await fireEvent.click(await screen.findByText('Ajouter une date'))
            const existingStock = screen.getByTestId(`stock-item-${initialStock.id}`)

            let nbExpectedRows = 0
            nbExpectedRows += 1 // header row
            nbExpectedRows += 1 // existing stock row
            nbExpectedRows += 1 // creation stock row
            expect(screen.getAllByRole('row')).toHaveLength(nbExpectedRows)

            // When
            await act(async () => {
              const existingStockScreen = within(existingStock)
              userEvent.click(await existingStockScreen.findByTitle('Supprimer le stock'))
              await userEvent.click(await screen.findByRole('button', { name: 'Supprimer' }))
            })

            // Then
            expect(screen.queryByTestId(`stock-item-${initialStock.id}`)).not.toBeInTheDocument()
            nbExpectedRows = 0
            nbExpectedRows += 1 // header row
            nbExpectedRows += 1 // creation stock row
            expect(screen.getAllByRole('row')).toHaveLength(nbExpectedRows)
          })

          it('should display a success message after deletion', async () => {
            // Given
            await renderOffers(props, store)

            // When
            userEvent.click(screen.getByTitle('Supprimer le stock'))
            userEvent.click(screen.getByRole('button', { name: 'Supprimer' }))

            // Then
            expect(await screen.findByText('Le stock a été supprimé.')).toBeInTheDocument()
          })

          it('should display an error message when deletion fails', async () => {
            // Given
            pcapi.deleteStock.mockRejectedValue({})
            await renderOffers(props, store)

            // When
            userEvent.click(screen.getByTitle('Supprimer le stock'))
            userEvent.click(screen.getByRole('button', { name: 'Supprimer' }))

            // Then
            expect(
              await screen.findByText('Une erreur est survenue lors de la suppression du stock.')
            ).toBeInTheDocument()
          })

          it('should disable deleting button', async () => {
            // given
            await renderOffers(props, store)

            // when
            await act(async () => {
              userEvent.click(await screen.findByTitle('Supprimer le stock'))
            })

            // then
            expect(screen.getByTitle('Supprimer le stock').closest('button')).toBeDisabled()
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

          pcapi.loadOffer.mockResolvedValue(eventOfferFromAllocine)
        })

        describe('when editing stock', () => {
          it('should be able to update price and quantity but not beginning date nor hour fields', async () => {
            // When
            await renderOffers(props, store)

            // Then
            expect(screen.getByLabelText('Date de l’événement')).toBeDisabled()
            expect(screen.getByLabelText('Heure de l’événement')).toBeDisabled()
            expect(screen.getByLabelText('Date limite de réservation')).toBeEnabled()
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
        pcapi.loadOffer.mockResolvedValue(thingOffer)
        pcapi.loadStocks.mockResolvedValue({ stocks: [thingStock] })
      })

      describe('when offer has been manually created', () => {
        it('should be able to edit price field', async () => {
          // given
          await renderOffers(props, store)
          const priceField = screen.getByDisplayValue('10.01')

          // when
          userEvent.clear(priceField)
          userEvent.type(priceField, '127.03')

          // then
          expect(screen.queryByDisplayValue('10.01')).not.toBeInTheDocument()
          expect(screen.getByDisplayValue('127.03')).toBeInTheDocument()
        })

        it('should be able to edit booking limit date field', async () => {
          // given
          await renderOffers(props, store)

          // when
          userEvent.click(screen.getByDisplayValue('18/12/2020'))
          userEvent.click(screen.getByText('17'))

          // then
          expect(screen.queryByDisplayValue('18/12/2020')).not.toBeInTheDocument()
          expect(screen.getByDisplayValue('17/12/2020')).toBeInTheDocument()
        })

        it('should be able to edit total quantity field', async () => {
          // given
          await renderOffers(props, store)
          const quantityField = screen.getByDisplayValue('10')

          // when
          userEvent.clear(quantityField)
          userEvent.type(quantityField, '23')

          // then
          expect(screen.queryByDisplayValue('10')).not.toBeInTheDocument()
          expect(screen.getByDisplayValue('23')).toBeInTheDocument()
        })

        it('should compute remaining quantity based on inputted total quantity', async () => {
          // given
          await renderOffers(props, store)
          const quantityField = screen.getByDisplayValue('10')

          // when
          userEvent.clear(quantityField)
          userEvent.type(quantityField, '9')

          // then
          const initialRemainingQuantity = screen.queryByText(6)
          expect(initialRemainingQuantity).not.toBeInTheDocument()

          const computedRemainingQuantity = screen.queryByText('5')
          expect(computedRemainingQuantity).toBeInTheDocument()
        })

        it('should set remaining quantity to Illimité when emptying total quantity field', async () => {
          // given
          await renderOffers(props, store)

          // when
          userEvent.clear(screen.getByDisplayValue('10'))

          // then
          const computedRemainingQuantity = screen.getByText('Illimité')
          expect(computedRemainingQuantity).toBeInTheDocument()
        })

        it('should not set remaining quantity to Illimité when total quantity is zero', async () => {
          // given
          pcapi.loadStocks.mockResolvedValue({
            stocks: [{ ...defaultStock, quantity: 0, bookingsQuantity: 0 }],
          })

          // when
          await renderOffers(props, store)

          // then
          expect(screen.getByLabelText('Quantité').value).not.toBe('')
          expect(screen.getByLabelText('Quantité').value).toBe('0')
          const remainingQuantityValue = screen.getAllByRole('cell')[3].textContent
          expect(remainingQuantityValue).not.toBe('Illimité')
          expect(remainingQuantityValue).toBe('0')
        })

        describe('when clicking on submit button', () => {
          it('should save changes done to stock', async () => {
            // Given
            pcapi.bulkCreateOrEditStock.mockResolvedValue({})
            await renderOffers(props, store)

            const priceField = screen.getByLabelText('Prix')
            userEvent.clear(priceField)
            userEvent.type(priceField, '14.01')

            userEvent.click(screen.getByLabelText('Date limite de réservation'))
            userEvent.click(screen.getByText('25'))

            const quantityField = screen.getByLabelText('Quantité')
            userEvent.clear(quantityField)
            userEvent.type(quantityField, '6')

            // When
            userEvent.click(screen.getByText('Enregistrer'))

            // Then
            expect(pcapi.bulkCreateOrEditStock).toHaveBeenCalledWith(defaultOffer.id, [
              {
                bookingLimitDatetime: '2020-12-26T02:59:59Z',
                id: '2E',
                price: '14.01',
                quantity: '6',
              },
            ])
            expect(screen.getByLabelText('Prix').value).toBe('14.01')
            expect(screen.getByLabelText('Date limite de réservation').value).toBe('25/12/2020')
            expect(screen.getByLabelText('Quantité').value).toBe('6')
          })

          it('should refresh stocks', async () => {
            // Given
            pcapi.bulkCreateOrEditStock.mockResolvedValue({})
            const initialStock = {
              ...defaultStock,
              price: 10.01,
            }
            const updatedStock = {
              ...defaultStock,
              price: 10,
            }
            pcapi.loadStocks
              .mockResolvedValueOnce({ stocks: [initialStock] })
              .mockResolvedValueOnce({ stocks: [updatedStock] })
            await renderOffers(props, store)
            pcapi.loadStocks.mockClear()

            // When
            await act(async () => {
              await userEvent.click(screen.getByText('Enregistrer'))
            })

            // Then
            expect(pcapi.loadStocks).toHaveBeenCalledTimes(1)
          })

          it('should set booking limit time to end of selected local day when specified in Cayenne TZ', async () => {
            // Given
            pcapi.bulkCreateOrEditStock.mockResolvedValue({})
            await renderOffers(props, store)
            userEvent.click(screen.getByLabelText('Date limite de réservation'))
            userEvent.click(screen.getByText('19'))

            // When
            userEvent.click(screen.getByText('Enregistrer'))

            // Then
            const savedStocks = pcapi.bulkCreateOrEditStock.mock.calls[0][1]
            expect(savedStocks[0].bookingLimitDatetime).toBe('2020-12-20T02:59:59Z')
          })

          it('should set booking limit time to end of selected local day when specified in Paris TZ', async () => {
            // Given
            thingOffer.venue.departementCode = '75'

            pcapi.bulkCreateOrEditStock.mockResolvedValue({})
            await renderOffers(props, store)
            userEvent.click(screen.getByLabelText('Date limite de réservation'))
            userEvent.click(screen.getByText('17'))

            // When
            userEvent.click(screen.getByText('Enregistrer'))

            // Then
            const savedStocks = pcapi.bulkCreateOrEditStock.mock.calls[0][1]
            expect(savedStocks[0].bookingLimitDatetime).toBe('2020-12-17T22:59:59Z')
          })

          it('should set booking limit datetime to null when not specified', async () => {
            // Given
            pcapi.bulkCreateOrEditStock.mockResolvedValue({})
            await renderOffers(props, store)
            userEvent.clear(screen.getByLabelText('Date limite de réservation'))

            // When
            userEvent.click(screen.getByText('Enregistrer'))

            // Then
            const savedStocks = pcapi.bulkCreateOrEditStock.mock.calls[0][1]
            expect(savedStocks[0].bookingLimitDatetime).toBeNull()
          })

          it('should set price to 0 when not specified', async () => {
            // Given
            pcapi.bulkCreateOrEditStock.mockResolvedValue({})
            await renderOffers(props, store)
            userEvent.clear(screen.getByLabelText('Prix'))

            // When
            userEvent.click(screen.getByText('Enregistrer'))
            // Then
            const savedStocks = pcapi.bulkCreateOrEditStock.mock.calls[0][1]
            expect(savedStocks[0].price).toBe(0)
          })

          it('should set quantity to null when not specified', async () => {
            // Given
            pcapi.bulkCreateOrEditStock.mockResolvedValue({})
            await renderOffers(props, store)
            userEvent.clear(screen.getByLabelText('Quantité'))

            // When
            userEvent.click(screen.getByText('Enregistrer'))
            // Then
            const savedStocks = pcapi.bulkCreateOrEditStock.mock.calls[0][1]
            expect(savedStocks[0].quantity).toBeNull()
          })

          it('should display error message on api error', async () => {
            // Given
            pcapi.bulkCreateOrEditStock.mockRejectedValueOnce({
              errors: {
                price: 'Le prix est invalide.',
                quantity: 'La quantité est invalide.',
              },
            })
            await renderOffers(props, store)

            userEvent.type(screen.getByLabelText('Quantité'), '10')

            // When
            await userEvent.click(screen.getByText('Enregistrer'))

            // Then
            const errorMessage = await screen.findByText(
              'Une ou plusieurs erreurs sont présentes dans le formulaire.'
            )
            expect(errorMessage).toBeInTheDocument()
          })

          it('should display error message on pre-submit error', async () => {
            // Given
            await renderOffers(props, store)

            userEvent.type(screen.getByLabelText('Prix'), '-10')
            userEvent.type(screen.getByLabelText('Quantité'), '-20')

            // When
            await userEvent.click(screen.getByText('Enregistrer'))

            // Then
            const errorMessage = await screen.findByText(
              'Une ou plusieurs erreurs sont présentes dans le formulaire.'
            )
            expect(errorMessage).toBeInTheDocument()
          })

          it('should display success message on success', async () => {
            // Given
            pcapi.bulkCreateOrEditStock.mockResolvedValue({})
            await renderOffers(props, store)

            userEvent.type(screen.getByLabelText('Quantité'), '10')

            // When
            await userEvent.click(screen.getByText('Enregistrer'))

            // Then
            const errorMessage = await screen.findByText('Vos stocks ont bien été sauvegardés.')
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
          pcapi.loadOffer.mockResolvedValue(synchronisedThingOffer)
        })

        it('should not be able to edit a stock', async () => {
          // When
          await renderOffers(props, store)

          // Then
          expect(screen.getByLabelText('Prix')).toBeDisabled()
          expect(screen.getByLabelText('Date limite de réservation')).toBeDisabled()
          expect(screen.getByLabelText('Quantité')).toBeDisabled()
        })

        it('should not be able to delete a stock', async () => {
          // When
          await renderOffers(props, store)

          // Then
          expect(screen.getByTestId('stock-delete-button')).toBeDisabled()
        })
      })
    })
  })

  describe('create', () => {
    it('should update displayed offer status', async () => {
      // Given
      const initialOffer = {
        ...defaultOffer,
        status: 'DRAFT',
      }
      const updatedOffer = {
        ...defaultOffer,
        status: 'ACTIVE',
      }
      pcapi.loadOffer.mockResolvedValueOnce(initialOffer).mockResolvedValueOnce(updatedOffer)
      pcapi.bulkCreateOrEditStock.mockResolvedValue({})

      // When
      await renderOffers(props, store)

      // Then
      expect(screen.queryByText('épuisée')).not.toBeInTheDocument()

      // When
      await act(async () => {
        await fireEvent.click(screen.getByText('Ajouter un stock'))
        await fireEvent.click(screen.getByText('Enregistrer'))
      })

      // Then
      expect(screen.getByText('active')).toBeInTheDocument()
    })

    describe('event offer', () => {
      let noStockOffer
      beforeEach(() => {
        noStockOffer = {
          ...defaultOffer,
          isEvent: true,
          stocks: [],
        }

        pcapi.loadOffer.mockResolvedValue(noStockOffer)
      })

      it('should not display remaining stocks and bookings columns when no stocks yet', async () => {
        // given
        const eventOffer = {
          ...defaultOffer,
          isEvent: true,
          stocks: [],
        }
        pcapi.loadOffer.mockResolvedValue(eventOffer)
        await renderOffers(props, store)

        // when
        userEvent.click(screen.getByText('Ajouter une date'))

        // then
        expect(screen.queryByText('Stock restant')).not.toBeInTheDocument()
        expect(screen.queryByText('Réservations')).not.toBeInTheDocument()
      })

      it('should append new stock line on top of stocks list when clicking on add button', async () => {
        // given
        const eventStock = {
          ...defaultStock,
          beginningDatetime: '2020-12-20T22:00:00Z',
        }
        pcapi.loadStocks.mockResolvedValue({ stocks: [eventStock] })
        await renderOffers(props, store)
        userEvent.click(screen.getByText('Ajouter une date'))

        // when
        userEvent.click(screen.getByText('Ajouter une date'))

        // then
        expect(screen.getAllByRole('row')).toHaveLength(4)
        const eventsDates = screen.getAllByLabelText('Date de l’événement')
        expect(eventsDates[0].value).toBe('')
        expect(eventsDates[1].value).toBe('')
        expect(eventsDates[2].value).toBe('20/12/2020')
      })

      it('should have date, hour, price, limit datetime and quantity fields emptied by default', async () => {
        // given
        await renderOffers(props, store)

        // when
        userEvent.click(screen.getByText('Ajouter une date'))

        // then
        expect(screen.getByLabelText('Date de l’événement').value).toBe('')
        expect(screen.getByLabelText('Heure de l’événement').value).toBe('')
        expect(screen.getByLabelText('Prix').value).toBe('')
        expect(screen.getByLabelText('Date limite de réservation').value).toBe('')
        expect(screen.getByLabelText('Quantité').value).toBe('')
      })

      it('should not have remaining stocks and bookings columns', async () => {
        // given
        await renderOffers(props, store)

        // when
        userEvent.click(screen.getByText('Ajouter une date'))

        // then
        const columnCells = screen.getAllByRole('cell')
        expect(columnCells[3].textContent).toBe('')
        expect(columnCells[4].textContent).toBe('')
      })

      it('should have a cancel button to cancel new stock', async () => {
        // given
        await renderOffers(props, store)

        // when
        userEvent.click(screen.getByText('Ajouter une date'))

        // then
        expect(screen.queryByTitle('Supprimer le stock')).toBeInTheDocument()
      })

      it('should add new stocks to stocks and remove new empty stock line when clicking on validate button', async () => {
        // given
        pcapi.bulkCreateOrEditStock.mockResolvedValue({})
        const createdStocks = [
          {
            quantity: 15,
            price: 15,
            remainingQuantity: 15,
            bookingsQuantity: 0,
            beginningDatetime: '2020-12-24T23:00:00Z',
            bookingLimitDatetime: '2020-12-22T23:59:59Z',
            id: '2E',
            isEventDeletable: true,
          },
          {
            quantity: 15,
            price: 15,
            remainingQuantity: 15,
            bookingsQuantity: 0,
            beginningDatetime: '2020-12-25T23:00:00Z',
            bookingLimitDatetime: '2020-12-23T23:59:59Z',
            id: '3E',
            isEventDeletable: true,
          },
        ]
        pcapi.loadStocks
          .mockResolvedValueOnce({ stocks: [] })
          .mockResolvedValueOnce({ stocks: createdStocks })
        await renderOffers(props, store)

        fireEvent.click(screen.getByText('Ajouter une date'))

        fireEvent.click(screen.getAllByLabelText('Date de l’événement')[0])
        fireEvent.click(screen.getByText('24'))

        fireEvent.click(screen.getAllByLabelText('Heure de l’événement')[0])
        fireEvent.click(screen.getByText('20:00'))

        fireEvent.change(screen.getByLabelText('Prix'), { target: { value: '15' } })

        fireEvent.click(screen.getAllByLabelText('Date limite de réservation')[0])
        fireEvent.click(screen.getByText('22'))

        fireEvent.change(screen.getByLabelText('Quantité'), { target: { value: '15' } })

        fireEvent.click(screen.getByText('Ajouter une date'))

        fireEvent.click(screen.getAllByLabelText('Date de l’événement')[0])
        fireEvent.click(screen.getByText('25'))

        fireEvent.click(screen.getAllByLabelText('Heure de l’événement')[0])
        fireEvent.click(screen.getByText('20:00'))

        fireEvent.click(screen.getAllByLabelText('Date limite de réservation')[0])
        fireEvent.click(screen.getByText('23'))

        // when
        await act(async () => {
          await fireEvent.click(screen.getByText('Enregistrer'))
        })

        // then
        expect(pcapi.bulkCreateOrEditStock).toHaveBeenCalledWith(defaultOffer.id, [
          {
            beginningDatetime: '2020-12-25T23:00:00Z',
            bookingLimitDatetime: '2020-12-24T02:59:59Z',
            price: 0,
            quantity: null,
          },
          {
            beginningDatetime: '2020-12-24T23:00:00Z',
            bookingLimitDatetime: '2020-12-23T02:59:59Z',
            price: '15',
            quantity: '15',
          },
        ])
        expect(screen.getAllByRole('row')).toHaveLength(3)
      })

      it('should cancel new stock addition when clicking on cancel button', async () => {
        // Given
        await renderOffers(props, store)
        userEvent.click(screen.getByText('Ajouter une date'))

        // When
        userEvent.click(screen.getByTitle('Supprimer le stock'))

        // Then
        expect(pcapi.bulkCreateOrEditStock).not.toHaveBeenCalled()
        expect(screen.queryByRole('row')).not.toBeInTheDocument()
      })

      it('should be able to add second stock while first one is not validated', async () => {
        // Given
        await renderOffers(props, store)

        // When
        userEvent.click(screen.getByText('Ajouter une date'))

        // Then
        expect(screen.getByText('Ajouter une date')).toBeEnabled()
      })

      it('should display error message on api error', async () => {
        // Given
        pcapi.bulkCreateOrEditStock.mockRejectedValueOnce({
          errors: {
            price: 'Le prix est invalide.',
            quantity: 'La quantité est invalide.',
          },
        })
        await renderOffers(props, store)
        userEvent.click(screen.getByText('Ajouter une date'))

        userEvent.click(screen.getByLabelText('Date de l’événement'))
        userEvent.click(screen.getByText('26'))

        userEvent.click(screen.getByLabelText('Heure de l’événement'))
        userEvent.click(screen.getByText('20:00'))

        // When
        await userEvent.click(screen.getByText('Enregistrer'))

        // Then
        const errorMessage = await screen.findByText(
          'Une ou plusieurs erreurs sont présentes dans le formulaire.'
        )
        expect(errorMessage).toBeInTheDocument()
      })

      it('should display error message on pre-submit error', async () => {
        // Given
        await renderOffers(props, store)
        userEvent.click(screen.getByText('Ajouter une date'))

        userEvent.click(screen.getByLabelText('Date de l’événement'))
        userEvent.click(screen.getByText('26'))

        userEvent.click(screen.getByLabelText('Heure de l’événement'))
        userEvent.click(screen.getByText('20:00'))

        userEvent.type(screen.getByLabelText('Prix'), '-10')
        userEvent.type(screen.getByLabelText('Quantité'), '-20')

        // When
        await userEvent.click(screen.getByText('Enregistrer'))

        // Then
        const errorMessage = await screen.findByText(
          'Une ou plusieurs erreurs sont présentes dans le formulaire.'
        )
        expect(errorMessage).toBeInTheDocument()
        expect(pcapi.bulkCreateOrEditStock).toHaveBeenCalledTimes(0)
      })

      it('should display success message on success', async () => {
        // Given
        pcapi.bulkCreateOrEditStock.mockResolvedValue({})
        await renderOffers(props, store)
        userEvent.click(screen.getByText('Ajouter une date'))

        userEvent.click(screen.getByLabelText('Date de l’événement'))
        userEvent.click(screen.getByText('26'))

        userEvent.click(screen.getByLabelText('Heure de l’événement'))
        userEvent.click(screen.getByText('20:00'))

        // When
        await userEvent.click(screen.getByText('Enregistrer'))

        // Then
        const errorMessage = await screen.findByText('Vos stocks ont bien été sauvegardés.')
        expect(errorMessage).toBeInTheDocument()
      })
    })

    describe('thing offer', () => {
      let noStockOffer
      beforeEach(() => {
        noStockOffer = {
          ...defaultOffer,
          isEvent: false,
          stocks: [],
        }

        pcapi.loadOffer.mockResolvedValue(noStockOffer)
      })

      it('should not display remaining stocks and bookings columns when no stocks yet', async () => {
        // given
        const thingOffer = {
          ...defaultOffer,
          isEvent: false,
          stocks: [],
        }
        pcapi.loadOffer.mockResolvedValue(thingOffer)
        await renderOffers(props, store)

        // when
        userEvent.click(screen.getByText('Ajouter un stock'))

        // then
        expect(screen.queryByText('Stock restant')).not.toBeInTheDocument()
        expect(screen.queryByText('Réservations')).not.toBeInTheDocument()
      })

      it('should append new stock line when clicking on add button', async () => {
        // given
        const thingOffer = {
          ...defaultOffer,
          isEvent: false,
          stocks: [],
        }
        pcapi.loadOffer.mockResolvedValue(thingOffer)
        await renderOffers(props, store)

        // when
        userEvent.click(screen.getByText('Ajouter un stock'))

        // then
        expect(screen.getAllByRole('row')).toHaveLength(2)
      })

      it('should have price, limit datetime and quantity fields emptied by default', async () => {
        // given
        await renderOffers(props, store)

        // when
        userEvent.click(screen.getByText('Ajouter un stock'))

        // then
        expect(screen.getByLabelText('Prix').value).toBe('')
        expect(screen.getByLabelText('Date limite de réservation').value).toBe('')
        expect(screen.getByLabelText('Quantité').value).toBe('')
      })

      it('should not have remaining stocks and bookings columns', async () => {
        // given
        await renderOffers(props, store)

        // when
        userEvent.click(screen.getByText('Ajouter un stock'))

        // then
        expect(screen.queryByText('Stock restant')).not.toBeInTheDocument()
        expect(screen.queryByText('Réservations')).not.toBeInTheDocument()
      })

      it('should have a cancel button to cancel new stock', async () => {
        // given
        await renderOffers(props, store)

        // when
        userEvent.click(screen.getByText('Ajouter un stock'))

        // then
        expect(screen.queryByTitle('Supprimer le stock')).toBeInTheDocument()
      })

      it('should add new stock to stocks and remove new empty stock line when clicking on validate button', async () => {
        // given
        pcapi.bulkCreateOrEditStock.mockResolvedValue({})
        const createdStock = {
          quantity: 15,
          price: 15,
          remainingQuantity: 15,
          bookingsQuantity: 0,
          bookingLimitDatetime: '2020-12-22T23:59:59Z',
          id: stockId,
        }
        pcapi.loadStocks
          .mockResolvedValueOnce({ stocks: [] })
          .mockResolvedValueOnce({ stocks: [createdStock] })
        await renderOffers(props, store)

        userEvent.click(screen.getByText('Ajouter un stock'))

        userEvent.type(screen.getByLabelText('Prix'), '15')

        userEvent.click(screen.getByLabelText('Date limite de réservation'))
        userEvent.click(screen.getByText('22'))

        userEvent.type(screen.getByLabelText('Quantité'), '15')

        // when
        await act(async () => {
          await userEvent.click(screen.getByText('Enregistrer'))
        })

        // then
        expect(pcapi.bulkCreateOrEditStock).toHaveBeenCalledWith('AG3A', [
          {
            bookingLimitDatetime: '2020-12-23T02:59:59Z',
            price: '15',
            quantity: '15',
          },
        ])
        expect(screen.getAllByRole('row')).toHaveLength(2)
      })

      it('should display error message on api error', async () => {
        // Given
        pcapi.bulkCreateOrEditStock.mockRejectedValue({
          errors: {
            price: 'Le prix est invalide.',
            quantity: 'La quantité est invalide.',
          },
        })
        await renderOffers(props, store)
        userEvent.click(screen.getByText('Ajouter un stock'))

        userEvent.type(screen.getByLabelText('Quantité'), '15')

        // When
        await userEvent.click(screen.getByText('Enregistrer'))

        // Then
        const errorMessage = await screen.findByText(
          'Une ou plusieurs erreurs sont présentes dans le formulaire.'
        )
        expect(errorMessage).toBeInTheDocument()
      })

      it('should display error message on pre-submit error', async () => {
        // Given
        await renderOffers(props, store)
        userEvent.click(screen.getByText('Ajouter un stock'))

        userEvent.type(screen.getByLabelText('Prix'), '-10')
        userEvent.type(screen.getByLabelText('Quantité'), '-20')

        // When
        await userEvent.click(screen.getByText('Enregistrer'))

        // Then
        const errorMessage = await screen.findByText(
          'Une ou plusieurs erreurs sont présentes dans le formulaire.'
        )
        expect(errorMessage).toBeInTheDocument()
        expect(pcapi.bulkCreateOrEditStock).toHaveBeenCalledTimes(0)
      })

      it('should display success message on success', async () => {
        // Given
        pcapi.bulkCreateOrEditStock.mockResolvedValue({})
        await renderOffers(props, store)
        userEvent.click(screen.getByText('Ajouter un stock'))

        userEvent.type(screen.getByLabelText('Quantité'), '15')

        // When
        await userEvent.click(screen.getByText('Enregistrer'))

        // Then
        const errorMessage = await screen.findByText('Vos stocks ont bien été sauvegardés.')
        expect(errorMessage).toBeInTheDocument()
      })

      it('should cancel new stock addition when clicking on cancel button', async () => {
        // Given
        await renderOffers(props, store)
        userEvent.click(screen.getByText('Ajouter un stock'))

        // When
        userEvent.click(screen.getByTitle('Supprimer le stock'))

        // Then
        expect(pcapi.bulkCreateOrEditStock).not.toHaveBeenCalled()
        expect(screen.queryByRole('row')).not.toBeInTheDocument()
      })
    })
  })
})
