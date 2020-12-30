import { fireEvent } from '@testing-library/dom'
import '@testing-library/jest-dom'
import { act, render, screen } from '@testing-library/react'
import moment from 'moment-timezone'
import React from 'react'
import { Provider } from 'react-redux'
import { MemoryRouter } from 'react-router'

import * as pcapi from 'repository/pcapi/pcapi'
import { configureTestStore } from 'store/testUtils'
import { queryByTextTrimHtml } from 'utils/testHelpers'

import Stocks from '../Stocks'

jest.mock('repository/pcapi/pcapi', () => ({
  deleteStock: jest.fn(),
  loadOffer: jest.fn(),
  updateStock: jest.fn(),
  createStock: jest.fn(),
}))

const renderStocks = (props, store) =>
  act(async () => {
    await render(
      <Provider store={store}>
        <MemoryRouter>
          <Stocks {...props} />
        </MemoryRouter>
      </Provider>
    )
  })

describe('stocks page', () => {
  let props
  let defaultOffer
  let defaultStock
  let spiedMomentSetDefaultTimezone
  let stockId
  let store
  beforeEach(() => {
    store = configureTestStore({ data: { users: [{ publicName: 'François', isAdmin: false }] } })
    jest.spyOn(Date.prototype, 'toISOString').mockImplementation(() => '2020-12-15T12:00:00Z')
    spiedMomentSetDefaultTimezone = jest.spyOn(moment.tz, 'setDefault')
    props = {
      offer: {
        id: 'AG3A',
      },
    }

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
    pcapi.deleteStock.mockResolvedValue({ id: stockId })
  })

  afterEach(() => {
    pcapi.loadOffer.mockReset()
    pcapi.deleteStock.mockReset()
    pcapi.updateStock.mockReset()
    pcapi.createStock.mockReset()
    spiedMomentSetDefaultTimezone.mockRestore()
  })

  describe('render', () => {
    it('should set timezone based on venue timezone', async () => {
      // Given
      pcapi.loadOffer.mockResolvedValue(defaultOffer)

      // When
      await renderStocks(props, store)

      // Then
      expect(spiedMomentSetDefaultTimezone).toHaveBeenCalledWith('America/Cayenne')
    })

    it('should display "Gratuit" when stock is free', async () => {
      // given
      const offerWithFreeStock = {
        ...defaultOffer,
        stocks: [
          {
            ...defaultStock,
            price: 0,
          },
        ],
      }

      pcapi.loadOffer.mockResolvedValue(offerWithFreeStock)

      // when
      await renderStocks(props, store)

      // then
      expect((await screen.findByPlaceholderText('Gratuit')).value).toBe('')
    })

    it('should display stocks sorted by descending beginning datetime', async () => {
      // given
      const offerWithMultipleStocks = {
        ...defaultOffer,
        isEvent: true,
        stocks: [
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
        ],
      }
      pcapi.loadOffer.mockResolvedValue(offerWithMultipleStocks)

      // when
      await renderStocks(props, store)

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
      const offerWithUnlimitedStock = {
        ...defaultOffer,
        stocks: [
          {
            ...defaultStock,
            quantity: null,
          },
        ],
      }

      pcapi.loadOffer.mockResolvedValue(offerWithUnlimitedStock)

      // when
      await renderStocks(props, store)

      // then
      expect((await screen.findByPlaceholderText('Illimité')).value).toBe('')
    })

    it('should display "Illimité" for remaining quantity when stock has unlimited quantity', async () => {
      // given
      const offerWithUnlimitedStock = {
        ...defaultOffer,
        stocks: [
          {
            ...defaultStock,
            quantity: null,
          },
        ],
      }

      pcapi.loadOffer.mockResolvedValue(offerWithUnlimitedStock)

      // when
      await renderStocks(props, store)

      // then
      expect(await screen.findByText('Illimité')).toBeInTheDocument()
    })

    it('should restore default timezone when unmounting', async () => {
      // Given
      let unmount
      await act(async () => {
        unmount = await render(
          <MemoryRouter>
            <Stocks offer={{ id: 'AG3A' }} />
          </MemoryRouter>
        ).unmount
      })

      // When
      unmount()

      // Then
      expect(spiedMomentSetDefaultTimezone).toHaveBeenCalledTimes(4)
      expect(spiedMomentSetDefaultTimezone).toHaveBeenNthCalledWith(1, 'Europe/Paris')
      expect(spiedMomentSetDefaultTimezone).toHaveBeenNthCalledWith(2)
      expect(spiedMomentSetDefaultTimezone).toHaveBeenNthCalledWith(3, 'America/Cayenne')
      expect(spiedMomentSetDefaultTimezone).toHaveBeenNthCalledWith(4)
    })

    describe('render event offer', () => {
      let eventOffer
      beforeEach(() => {
        eventOffer = {
          ...defaultOffer,
          isEvent: true,
          stocks: [
            {
              ...defaultStock,
              beginningDatetime: '2020-12-20T22:00:00Z',
            },
          ],
        }

        pcapi.loadOffer.mockResolvedValue(eventOffer)
      })

      afterEach(() => {
        pcapi.loadOffer.mockReset()
      })

      it('should display an information message regarding booking cancellation', async () => {
        // when
        await renderStocks(props, store)

        // then
        const informationMessage = screen.getByText(
          'Les utilisateurs ont un délai de 48h pour annuler leur réservation mais ne peuvent pas le faire moins de 48h avant le début de l’événement. Si la date limite de réservation n’est pas encore passée, la place est alors automatiquement remise en vente.'
        )
        expect(informationMessage).toBeInTheDocument()
      })

      it('should display button to add date', async () => {
        // when
        await renderStocks(props, store)

        // then
        const buttonAddDate = await screen.findByRole('button', { name: 'Ajouter une date' })
        expect(buttonAddDate).toBeInTheDocument()
      })

      it("should display offer's stocks fields disabled by default", async () => {
        // when
        await renderStocks(props, store)

        // then
        expect(pcapi.loadOffer).toHaveBeenCalledWith('AG3A')

        const columnHeaders = await screen.findAllByRole('columnheader')
        const columnCells = await screen.findAllByRole('cell')

        expect(columnHeaders).toHaveLength(9)

        expect(columnHeaders[0].textContent).toBe('Date')
        expect(columnCells[0].querySelector('input').value).toBe('20/12/2020')
        expect(columnCells[0].querySelector('input')).toBeDisabled()

        expect(columnHeaders[1].textContent).toBe('Horaire')
        expect(columnCells[1].querySelector('input').value).toBe('19:00')
        expect(columnCells[1].querySelector('input')).toBeDisabled()

        expect(columnHeaders[2].textContent).toBe('Prix')
        expect(columnCells[2].querySelector('input').value).toBe('10.01')
        expect(columnCells[2].querySelector('input')).toBeDisabled()

        expect(columnHeaders[3].textContent).toBe('Date limite de réservation')
        expect(columnCells[3].querySelector('input').value).toBe('18/12/2020')
        expect(columnCells[3].querySelector('input')).toBeDisabled()

        expect(columnHeaders[4].textContent).toBe('Quantité')
        expect(columnCells[4].querySelector('input').value).toBe('10')
        expect(columnCells[4].querySelector('input')).toBeDisabled()

        expect(columnHeaders[5].textContent).toBe('Stock restant')
        expect(columnCells[5].textContent).toBe('6')

        expect(columnHeaders[6].textContent).toBe('Réservations')
        expect(columnCells[6].textContent).toBe('4')

        expect(columnHeaders[7].textContent).toBe('Modifier')
        expect(columnCells[7].querySelector('img[alt="Modifier le stock"]')).toBeInTheDocument()

        expect(columnHeaders[8].textContent).toBe('Supprimer')
        expect(columnCells[8].querySelector('img[alt="Supprimer le stock"]')).toBeInTheDocument()
      })
    })

    describe('render thing offer', () => {
      let thingOffer
      beforeEach(() => {
        thingOffer = {
          ...defaultOffer,
          isEvent: false,
          stocks: [
            {
              ...defaultStock,
            },
          ],
        }
        pcapi.loadOffer.mockResolvedValue(thingOffer)
      })

      afterEach(() => {
        pcapi.loadOffer.mockReset()
      })

      it('should display an information message regarding booking cancellation', async () => {
        // when
        await renderStocks(props, store)

        // then
        const informationMessage = screen.getByText(
          'Les utilisateurs ont 30 jours pour faire valider leur contremarque. Passé ce délai, la réservation est automatiquement annulée et l’offre remise en vente.'
        )
        expect(informationMessage).toBeInTheDocument()
      })

      it('should display button to add stock', async () => {
        // given
        const thingOfferWithoutStock = { ...thingOffer, stocks: [] }
        pcapi.loadOffer.mockResolvedValue(thingOfferWithoutStock)

        // when
        await renderStocks(props, store)

        // then
        expect(screen.getByRole('button', { name: 'Ajouter un stock' })).toBeEnabled()
      })

      it('should not be able to add a new stock if there is already one', async () => {
        // When
        await renderStocks(props, store)

        // Then
        expect(screen.getByRole('button', { name: 'Ajouter un stock' })).toBeDisabled()
      })

      it("should display offer's stock fields disabled by default", async () => {
        // when
        await renderStocks(props, store)

        // then
        expect(pcapi.loadOffer).toHaveBeenCalledWith('AG3A')

        const columnHeaders = await screen.findAllByRole('columnheader')
        const columnCells = await screen.findAllByRole('cell')

        expect(columnHeaders).toHaveLength(7)

        expect(columnHeaders[0].textContent).toBe('Prix')
        expect(columnCells[0].querySelector('input').value).toBe('10.01')
        expect(columnCells[0].querySelector('input')).toBeDisabled()

        expect(columnHeaders[1].textContent).toBe('Date limite de réservation')
        expect(columnCells[1].querySelector('input').value).toBe('18/12/2020')
        expect(columnCells[1].querySelector('input')).toBeDisabled()

        expect(columnHeaders[2].textContent).toBe('Quantité')
        expect(columnCells[2].querySelector('input').value).toBe('10')
        expect(columnCells[2].querySelector('input')).toBeDisabled()

        expect(columnHeaders[3].textContent).toBe('Stock restant')
        expect(columnCells[3].textContent).toBe('6')

        expect(columnHeaders[4].textContent).toBe('Réservations')
        expect(columnCells[4].textContent).toBe('4')

        expect(columnHeaders[5].textContent).toBe('Modifier')
        expect(columnCells[5].querySelector('img[alt="Modifier le stock"]')).toBeInTheDocument()

        expect(columnHeaders[6].textContent).toBe('Supprimer')
        expect(columnCells[6].querySelector('img[alt="Supprimer le stock"]')).toBeInTheDocument()
      })

      describe('when offer has been synchronized', () => {
        beforeEach(() => {
          const synchronisedThingOfferWithoutStock = {
            ...defaultOffer,
            isEvent: false,
            lastProviderId: 'D4',
            stocks: [],
          }
          pcapi.loadOffer.mockResolvedValue(synchronisedThingOfferWithoutStock)
        })

        afterEach(() => {
          pcapi.loadOffer.mockReset()
        })

        it('should not be able to add a stock', async () => {
          // When
          await renderStocks(props, store)

          // Then
          expect(screen.getByRole('button', { name: 'Ajouter un stock' })).toBeDisabled()
        })
      })
    })
  })

  describe('edit', () => {
    describe('edit event offer', () => {
      let eventOffer
      beforeEach(() => {
        eventOffer = {
          ...defaultOffer,
          isEvent: true,
          stocks: [
            {
              ...defaultStock,
              beginningDatetime: '2020-12-20T22:00:00Z',
            },
          ],
        }

        pcapi.loadOffer.mockResolvedValue(eventOffer)
      })

      afterEach(() => {
        pcapi.loadOffer.mockReset()
      })

      describe('when offer has been manually created', () => {
        it('should not be able to edit a stock when expired', async () => {
          // Given
          const dayAfterBeginningDatetime = '2020-12-21T12:00:00Z'
          jest
            .spyOn(Date.prototype, 'toISOString')
            .mockImplementation(() => dayAfterBeginningDatetime)
          await renderStocks(props, store)

          // When
          fireEvent.click(screen.getByAltText('Modifier le stock'))

          // Then
          expect(screen.getByAltText('Modifier le stock').closest('button')).toBeDisabled()
          expect(screen.queryByAltText('Valider les modifications')).not.toBeInTheDocument()
          expect(screen.queryByAltText('Annuler les modifications')).not.toBeInTheDocument()
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
          await renderStocks(props, store)

          // When
          fireEvent.click(screen.getByAltText('Supprimer le stock'))

          // Then
          expect(screen.getByAltText('Supprimer le stock').closest('button')).toBeDisabled()
          expect(pcapi.deleteStock).not.toHaveBeenCalled()
        })

        describe('when editing stock', () => {
          it('should be able to edit beginning date field', async () => {
            // given
            await renderStocks(props, store)
            fireEvent.click(screen.getByAltText('Modifier le stock'))

            // when
            fireEvent.click(screen.getByDisplayValue('20/12/2020'))
            fireEvent.click(screen.getByLabelText('day-21'))

            // then
            expect(screen.queryByDisplayValue('20/12/2020')).not.toBeInTheDocument()
            expect(screen.getByDisplayValue('21/12/2020')).toBeInTheDocument()
          })

          it('should not be able to select beginning date before today', async () => {
            // given
            await renderStocks(props, store)
            fireEvent.click(screen.getByAltText('Modifier le stock'))

            // when
            fireEvent.click(screen.getByDisplayValue('20/12/2020'))
            fireEvent.click(screen.getByLabelText('day-13'))

            // then
            expect(screen.queryByDisplayValue('13/12/2020')).not.toBeInTheDocument()
            expect(screen.getByDisplayValue('20/12/2020')).toBeInTheDocument()
          })

          it('should be able to edit hour field', async () => {
            // given
            await renderStocks(props, store)
            fireEvent.click(screen.getByAltText('Modifier le stock'))

            // when
            fireEvent.click(screen.getByDisplayValue('19:00'))
            fireEvent.click(screen.getByText('18:30'))

            // then
            expect(screen.queryByDisplayValue('19:00')).not.toBeInTheDocument()
            expect(screen.getByDisplayValue('18:30')).toBeInTheDocument()
          })

          it('should be able to edit price field', async () => {
            // given
            await renderStocks(props, store)
            fireEvent.click(screen.getByAltText('Modifier le stock'))

            // when
            fireEvent.change(screen.getByDisplayValue('10.01'), { target: { value: '127.03' } })

            // then
            expect(screen.queryByDisplayValue('10.01')).not.toBeInTheDocument()
            expect(screen.getByDisplayValue('127.03')).toBeInTheDocument()
          })

          it('should be able to edit booking limit date field', async () => {
            // given
            await renderStocks(props, store)
            fireEvent.click(screen.getByAltText('Modifier le stock'))

            // when
            fireEvent.click(screen.getByDisplayValue('18/12/2020'))
            fireEvent.click(screen.getByLabelText('day-17'))

            // then
            expect(screen.queryByDisplayValue('18/12/2020')).not.toBeInTheDocument()
            expect(screen.getByDisplayValue('17/12/2020')).toBeInTheDocument()
          })

          it('should not be able to select booking limit date after beginning date', async () => {
            // given
            await renderStocks(props, store)
            fireEvent.click(screen.getByAltText('Modifier le stock'))

            // when
            fireEvent.click(screen.getByDisplayValue('18/12/2020'))
            fireEvent.click(screen.getByLabelText('day-21'))

            // then
            expect(screen.queryByDisplayValue('21/12/2020')).not.toBeInTheDocument()
            expect(screen.getByDisplayValue('18/12/2020')).toBeInTheDocument()
          })

          it('should set booking limit datetime to beginning datetime when selecting a beginning datetime prior to booking limit datetime', async () => {
            // given
            await renderStocks(props, store)
            fireEvent.click(screen.getByAltText('Modifier le stock'))

            // when
            fireEvent.click(screen.getByDisplayValue('20/12/2020'))
            fireEvent.click(screen.getByLabelText('day-17'))

            // then
            expect(screen.getByLabelText('Date limite de réservation').value).toBe('17/12/2020')
          })

          it('should be able to edit total quantity field', async () => {
            // given
            await renderStocks(props, store)
            fireEvent.click(screen.getByAltText('Modifier le stock'))

            // when
            fireEvent.change(screen.getByDisplayValue('10'), { target: { value: '23' } })

            // then
            expect(screen.queryByDisplayValue('10')).not.toBeInTheDocument()
            expect(screen.getByDisplayValue('23')).toBeInTheDocument()
          })

          it('should compute remaining quantity based on inputted total quantity', async () => {
            // given
            await renderStocks(props, store)
            fireEvent.click(screen.getByAltText('Modifier le stock'))

            // when
            fireEvent.change(screen.getByDisplayValue('10'), { target: { value: '9' } })

            // then
            const initialRemainingQuantity = screen.queryByText('6')
            expect(initialRemainingQuantity).not.toBeInTheDocument()

            const computedRemainingQuantity = screen.queryByText('5')
            expect(computedRemainingQuantity).toBeInTheDocument()
          })

          it('should set remaining quantity to Illimité when emptying total quantity field', async () => {
            // given
            await renderStocks(props, store)
            fireEvent.click(screen.getByAltText('Modifier le stock'))

            // when
            fireEvent.change(screen.getByDisplayValue('10'), { target: { value: '' } })

            // then
            const computedRemainingQuantity = screen.getByText('Illimité')
            expect(computedRemainingQuantity).toBeInTheDocument()
          })

          it('should not set remaining quantity to Illimité when total quantity is zero', async () => {
            // given
            pcapi.loadOffer.mockResolvedValue({
              ...eventOffer,
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
            await renderStocks(props, store)

            // then
            expect(screen.getByLabelText('Quantité').value).not.toBe('')
            expect(screen.getByLabelText('Quantité').value).toBe('0')
            const remainingQuantityValue = screen.getAllByRole('cell')[5].textContent
            expect(remainingQuantityValue).not.toBe('Illimité')
            expect(remainingQuantityValue).toBe('0')
          })

          it('should display a validation button instead of an edition button', async () => {
            // given
            await renderStocks(props, store)

            // when
            fireEvent.click(screen.getByAltText('Modifier le stock'))

            // then
            expect(screen.getByAltText('Valider les modifications')).toBeInTheDocument()
            expect(screen.queryByAltText('Modifier le stock')).not.toBeInTheDocument()
          })

          it('should display a cancellation button instead of a deletion button', async () => {
            // given
            await renderStocks(props, store)

            // when
            fireEvent.click(screen.getByAltText('Modifier le stock'))

            // then
            expect(screen.getByAltText('Annuler les modifications')).toBeInTheDocument()
            expect(screen.queryByAltText('Supprimer le stock')).not.toBeInTheDocument()
          })

          it('should discard changes on stock when clicking on cancel button', async () => {
            // Given
            await renderStocks(props, store)
            fireEvent.click(screen.getByAltText('Modifier le stock'))

            fireEvent.click(screen.getByLabelText('Date de l’événement'))
            fireEvent.click(screen.getByLabelText('day-26'))

            fireEvent.click(screen.getByLabelText('Heure de l’événement'))
            fireEvent.click(screen.getByText('20:00'))

            fireEvent.change(screen.getByLabelText('Prix'), { target: { value: '14.01' } })

            fireEvent.click(screen.getByLabelText('Date limite de réservation'))
            fireEvent.click(screen.getByLabelText('day-25'))

            fireEvent.change(screen.getByLabelText('Quantité'), { target: { value: '6' } })

            // When
            fireEvent.click(screen.getByAltText('Annuler les modifications'))

            // Then
            expect(pcapi.updateStock).not.toHaveBeenCalled()
            expect(screen.getByLabelText('Date de l’événement').value).toBe('20/12/2020')
            expect(screen.getByLabelText('Heure de l’événement').value).toBe('19:00')
            expect(screen.getByLabelText('Prix').value).toBe('10.01')
            expect(screen.getByLabelText('Date limite de réservation').value).toBe('18/12/2020')
            expect(screen.getByLabelText('Quantité').value).toBe('10')
          })

          it('should exit edition mode on discard changes', async () => {
            // Given
            await renderStocks(props, store)
            fireEvent.click(screen.getByAltText('Modifier le stock'))

            // When
            fireEvent.click(screen.getByAltText('Annuler les modifications'))

            // Then
            expect(screen.queryByAltText('Valider les modifications')).not.toBeInTheDocument()
            expect(screen.queryByAltText('Annuler les modifications')).not.toBeInTheDocument()
          })

          it('should not be able to validate changes when beginning date field is empty', async () => {
            // given
            await renderStocks(props, store)
            fireEvent.click(screen.getByAltText('Modifier le stock'))
            fireEvent.change(screen.getByDisplayValue('20/12/2020'), { target: { value: '' } })

            // when
            fireEvent.click(screen.getByAltText('Valider les modifications'))

            // then
            expect(
              screen.getByAltText('Valider les modifications').closest('button')
            ).toBeDisabled()
            expect(pcapi.updateStock).not.toHaveBeenCalled()
          })

          it('should not be able to validate changes when hour field is empty', async () => {
            // given
            await renderStocks(props, store)
            fireEvent.click(screen.getByAltText('Modifier le stock'))
            fireEvent.change(screen.getByDisplayValue('19:00'), { target: { value: '' } })

            // when
            fireEvent.click(screen.getByAltText('Valider les modifications'))

            // then
            expect(
              screen.getByAltText('Valider les modifications').closest('button')
            ).toBeDisabled()
            expect(pcapi.updateStock).not.toHaveBeenCalled()
          })

          describe('when clicking on validate button', () => {
            it('should save changes done to stock', async () => {
              // Given
              pcapi.updateStock.mockResolvedValue({})
              await renderStocks(props, store)
              fireEvent.click(screen.getByAltText('Modifier le stock'))

              fireEvent.click(screen.getByLabelText('Date de l’événement'))
              fireEvent.click(screen.getByLabelText('day-26'))

              fireEvent.click(screen.getByLabelText('Heure de l’événement'))
              fireEvent.click(screen.getByText('20:00'))

              fireEvent.change(screen.getByLabelText('Prix'), { target: { value: '14.01' } })

              fireEvent.click(screen.getByLabelText('Date limite de réservation'))
              fireEvent.click(screen.getByLabelText('day-25'))

              fireEvent.change(screen.getByLabelText('Quantité'), { target: { value: '6' } })

              // When
              fireEvent.click(screen.getByAltText('Valider les modifications'))

              // Then
              expect(pcapi.updateStock).toHaveBeenCalledWith({
                beginningDatetime: '2020-12-26T23:00:00Z',
                bookingLimitDatetime: '2020-12-25T23:59:59Z',
                id: '2E',
                price: '14.01',
                quantity: '6',
              })
              expect(screen.getByLabelText('Date de l’événement').value).toBe('26/12/2020')
              expect(screen.getByLabelText('Heure de l’événement').value).toBe('20:00')
              expect(screen.getByLabelText('Prix').value).toBe('14.01')
              expect(screen.getByLabelText('Date limite de réservation').value).toBe('25/12/2020')
              expect(screen.getByLabelText('Quantité').value).toBe('6')
            })

            it('should refresh offer and leave edition mode', async () => {
              // Given
              pcapi.updateStock.mockResolvedValue({})
              const offer = {
                ...defaultOffer,
                isEvent: true,
              }
              const stock = {
                ...defaultStock,
                beginningDatetime: '2020-12-20T22:00:00Z',
              }
              const initialOffer = {
                ...offer,
                stocks: [
                  {
                    ...stock,
                    price: 10.01,
                  },
                ],
              }
              const updatedOffer = {
                ...offer,
                stocks: [
                  {
                    ...stock,
                    price: 10,
                  },
                ],
              }
              pcapi.loadOffer
                .mockResolvedValueOnce(initialOffer)
                .mockResolvedValueOnce(updatedOffer)
              await renderStocks(props, store)
              fireEvent.click(screen.getByAltText('Modifier le stock'))

              // When
              await act(async () => {
                await fireEvent.click(screen.getByAltText('Valider les modifications'))
              })

              // Then
              expect(pcapi.loadOffer).toHaveBeenCalledTimes(2)
              expect(screen.queryByAltText('Valider les modifications')).not.toBeInTheDocument()
              expect(screen.queryByAltText('Annuler les modifications')).not.toBeInTheDocument()
            })

            it('should set booking limit datetime to exact beginning datetime when not specified or same as beginning date', async () => {
              // Given
              pcapi.updateStock.mockResolvedValue({})
              await renderStocks(props, store)
              fireEvent.click(screen.getByAltText('Modifier le stock'))
              fireEvent.change(screen.getByLabelText('Date limite de réservation'), {
                target: { value: '' },
              })

              // When
              fireEvent.click(screen.getByAltText('Valider les modifications'))

              // Then
              expect(pcapi.updateStock.mock.calls[0][0].bookingLimitDatetime).toBe(
                '2020-12-20T22:00:00Z'
              )
            })

            it('should set booking limit datetime to exact beginning datetime when same as beginning date', async () => {
              // Given
              pcapi.updateStock.mockResolvedValue({})
              await renderStocks(props, store)
              fireEvent.click(screen.getByAltText('Modifier le stock'))
              fireEvent.click(screen.getByLabelText('Date limite de réservation'))
              fireEvent.click(screen.getByLabelText('day-20'))

              // When
              fireEvent.click(screen.getByAltText('Valider les modifications'))

              // Then
              expect(pcapi.updateStock.mock.calls[0][0].bookingLimitDatetime).toBe(
                '2020-12-20T22:00:00Z'
              )
            })

            it('should set booking limit time to end of selected day when specified and different than beginning date', async () => {
              // Given
              pcapi.updateStock.mockResolvedValue({})
              await renderStocks(props, store)
              fireEvent.click(screen.getByAltText('Modifier le stock'))
              fireEvent.click(screen.getByLabelText('Date limite de réservation'))
              fireEvent.click(screen.getByLabelText('day-19'))

              // When
              fireEvent.click(screen.getByAltText('Valider les modifications'))
              // Then
              expect(pcapi.updateStock.mock.calls[0][0].bookingLimitDatetime).toBe(
                '2020-12-19T23:59:59Z'
              )
            })

            it('should set price to 0 when not specified', async () => {
              // Given
              pcapi.updateStock.mockResolvedValue({})
              await renderStocks(props, store)
              fireEvent.click(screen.getByAltText('Modifier le stock'))
              fireEvent.change(screen.getByLabelText('Prix'), { target: { value: '' } })

              // When
              fireEvent.click(screen.getByAltText('Valider les modifications'))
              // Then
              expect(pcapi.updateStock.mock.calls[0][0].price).toBe(0)
            })

            it('should set quantity to null when not specified', async () => {
              // Given
              pcapi.updateStock.mockResolvedValue({})
              await renderStocks(props, store)
              fireEvent.click(screen.getByAltText('Modifier le stock'))
              fireEvent.change(screen.getByLabelText('Quantité'), { target: { value: '' } })

              // When
              fireEvent.click(screen.getByAltText('Valider les modifications'))
              // Then
              expect(pcapi.updateStock.mock.calls[0][0].quantity).toBeNull()
            })
          })
        })

        describe('when deleting stock', () => {
          it('should display confirmation dialog box with focus on confirmation button', async () => {
            // Given
            await renderStocks(props, store)

            // When
            fireEvent.click(screen.getByAltText('Supprimer le stock'))

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
            await renderStocks(props, store)

            // When
            fireEvent.click(screen.getByAltText('Supprimer le stock'))
            fireEvent.click(screen.getByRole('button', { name: 'Supprimer' }))

            // Then
            expect(pcapi.deleteStock).toHaveBeenCalledWith(stockId)
          })

          it('should not delete stock if aborting on confirmation', async () => {
            // Given
            await renderStocks(props, store)

            // When
            fireEvent.click(screen.getByAltText('Supprimer le stock'))
            fireEvent.click(screen.getByRole('button', { name: 'Annuler' }))

            // Then
            expect(pcapi.deleteStock).not.toHaveBeenCalled()
          })

          it('should discard deleted stock from list', async () => {
            // Given
            const eventOffer = {
              ...defaultOffer,
              isEvent: true,
              stocks: [
                {
                  ...defaultStock,
                  beginningDatetime: '2020-12-20T22:00:00Z',
                },
              ],
            }
            const eventOfferWithoutStock = {
              ...defaultOffer,
              isEvent: true,
              stocks: [],
            }
            pcapi.loadOffer
              .mockResolvedValueOnce(eventOffer)
              .mockResolvedValueOnce(eventOfferWithoutStock)

            await renderStocks(props, store)

            // When
            await act(async () => {
              fireEvent.click(await screen.findByAltText('Supprimer le stock'))
              await fireEvent.click(screen.getByRole('button', { name: 'Supprimer' }))
            })

            // Then
            expect(screen.getAllByRole('row')).toHaveLength(1)
          })

          it('should disable editing and deleting buttons', async () => {
            // given
            await renderStocks(props, store)

            // when
            await act(async () => {
              fireEvent.click(await screen.findByAltText('Supprimer le stock'))
            })

            // then
            expect(screen.getByAltText('Modifier le stock').closest('button')).toBeDisabled()
            expect(screen.getByAltText('Supprimer le stock').closest('button')).toBeDisabled()
          })
        })
      })

      describe('when offer has been synchronized with Allocine', () => {
        beforeEach(() => {
          const eventOfferFromAllocine = {
            ...eventOffer,
            lastProviderId: 'CY',
          }

          pcapi.loadOffer.mockResolvedValue(eventOfferFromAllocine)
        })

        afterEach(() => {
          pcapi.loadOffer.mockReset()
        })

        describe('when editing stock', () => {
          it('should not be able to update beginning date nor hour fields', async () => {
            // Given
            await renderStocks(props, store)

            // When
            fireEvent.click(screen.getByAltText('Modifier le stock'))

            // Then
            expect(screen.getByLabelText('Date de l’événement')).toBeDisabled()
            expect(screen.getByLabelText('Heure de l’événement')).toBeDisabled()
            expect(screen.getByLabelText('Date limite de réservation')).toBeEnabled()
            expect(screen.getByLabelText('Prix')).toBeEnabled()
            expect(screen.getByLabelText('Quantité')).toBeEnabled()
          })
        })
      })

      describe('create new stock', () => {
        let noStockOffer
        beforeEach(() => {
          noStockOffer = {
            ...defaultOffer,
            isEvent: true,
            stocks: [],
          }

          pcapi.loadOffer.mockResolvedValue(noStockOffer)
        })

        afterEach(() => {
          pcapi.loadOffer.mockReset()
        })

        it('should append new stock line on top of stocks list when clicking on add button', async () => {
          // given
          const eventOffer = {
            ...defaultOffer,
            isEvent: true,
            stocks: [
              {
                ...defaultStock,
                beginningDatetime: '2020-12-20T22:00:00Z',
              },
            ],
          }
          pcapi.loadOffer.mockResolvedValue(eventOffer)
          await renderStocks(props, store)

          // when
          fireEvent.click(screen.getByText('Ajouter une date'))

          // then
          expect(screen.getAllByRole('row')).toHaveLength(3)
          expect(screen.getAllByLabelText('Date de l’événement')[0].value).toBe('')
          expect(screen.getAllByLabelText('Date de l’événement')[1].value).toBe('20/12/2020')
        })

        it('should have empty date, hour, price, limit datetime and quantity fields emptied by default', async () => {
          // given
          await renderStocks(props, store)

          // when
          fireEvent.click(screen.getByText('Ajouter une date'))

          // then
          expect(screen.getByLabelText('Date de l’événement').value).toBe('')
          expect(screen.getByLabelText('Heure de l’événement').value).toBe('')
          expect(screen.getByLabelText('Prix').value).toBe('')
          expect(screen.getByLabelText('Date limite de réservation').value).toBe('')
          expect(screen.getByLabelText('Quantité').value).toBe('')
        })

        it('should not have remaining stocks and bookings columns', async () => {
          // given
          await renderStocks(props, store)

          // when
          fireEvent.click(screen.getByText('Ajouter une date'))

          // then
          const columnCells = screen.getAllByRole('cell')
          expect(columnCells[3].textContent).toBe('')
          expect(columnCells[4].textContent).toBe('')
        })

        it('should not have edit and delete columns', async () => {
          // given
          await renderStocks(props, store)

          // when
          fireEvent.click(screen.getByText('Ajouter une date'))

          // then
          expect(screen.queryByAltText('Modifier le stock')).not.toBeInTheDocument()
          expect(screen.queryByAltText('Supprimer le stock')).not.toBeInTheDocument()
        })

        it('should have a validation and cancel button to save or cancel new stock', async () => {
          // given
          await renderStocks(props, store)

          // when
          fireEvent.click(screen.getByText('Ajouter une date'))

          // then
          expect(screen.queryByAltText('Valider les modifications')).toBeInTheDocument()
          expect(screen.queryByAltText('Annuler les modifications')).toBeInTheDocument()
        })

        it('should not be able to validate while beginning date time is empty', async () => {
          // given
          await renderStocks(props, store)

          // when
          fireEvent.click(screen.getByText('Ajouter une date'))

          // then
          expect(
            screen.queryByAltText('Valider les modifications').closest('button')
          ).toBeDisabled()

          fireEvent.click(screen.getByLabelText('Date de l’événement'))
          fireEvent.click(screen.getByLabelText('day-24'))
          expect(screen.queryByAltText('Valider les modifications').closest('button')).toBeEnabled()
        })

        it('should add new stock to stocks and remove new empty stock line when clicking on validate button', async () => {
          // given
          pcapi.createStock.mockResolvedValue({})
          const offer = {
            ...defaultOffer,
            isEvent: true,
          }
          const initialOffer = {
            ...offer,
            stocks: [],
          }
          const updatedOffer = {
            ...offer,
            stocks: [
              {
                quantity: 15,
                price: 15,
                remainingQuantity: 15,
                bookingsQuantity: 0,
                beginningDatetime: '2020-12-24T23:00:00Z',
                bookingLimitDatetime: '2020-12-22T23:59:59Z',
                id: stockId,
                isEventDeletable: true,
              },
            ],
          }
          pcapi.loadOffer.mockResolvedValueOnce(initialOffer).mockResolvedValueOnce(updatedOffer)
          await renderStocks(props, store)

          fireEvent.click(screen.getByText('Ajouter une date'))

          fireEvent.click(screen.getByLabelText('Date de l’événement'))
          fireEvent.click(screen.getByLabelText('day-24'))

          fireEvent.click(screen.getByLabelText('Heure de l’événement'))
          fireEvent.click(screen.getByText('20:00'))

          fireEvent.change(screen.getByLabelText('Prix'), { target: { value: '15' } })

          fireEvent.click(screen.getByLabelText('Date limite de réservation'))
          fireEvent.click(screen.getByLabelText('day-22'))

          fireEvent.change(screen.getByLabelText('Quantité'), { target: { value: '15' } })

          // when
          await act(async () => {
            await fireEvent.click(screen.getByAltText('Valider les modifications'))
          })

          // then
          expect(pcapi.createStock).toHaveBeenCalledWith({
            offerId: 'AG3A',
            beginningDatetime: '2020-12-24T23:00:00Z',
            bookingLimitDatetime: '2020-12-22T23:59:59Z',
            price: '15',
            quantity: '15',
          })
          expect(screen.getAllByRole('row')).toHaveLength(2)
        })

        it('should cancel new stock addition when clicking on cancel button', async () => {
          // Given
          await renderStocks(props, store)
          fireEvent.click(screen.getByText('Ajouter une date'))

          // When
          fireEvent.click(screen.getByAltText('Annuler les modifications'))

          // Then
          expect(pcapi.createStock).not.toHaveBeenCalled()
          expect(screen.getAllByRole('row')).toHaveLength(1)
        })

        it('should not be able to add second stock while first one is not validated', async () => {
          // Given
          await renderStocks(props, store)

          // When
          fireEvent.click(screen.getByText('Ajouter une date'))

          // Then
          expect(screen.getByText('Ajouter une date')).toBeDisabled()
        })
      })
    })

    describe('edit thing offer', () => {
      let thingOffer
      beforeEach(() => {
        thingOffer = {
          ...defaultOffer,
          isEvent: false,
          stocks: [
            {
              ...defaultStock,
              isEventDeletable: true,
            },
          ],
        }
        pcapi.loadOffer.mockResolvedValue(thingOffer)
      })

      afterEach(() => {
        pcapi.loadOffer.mockReset()
      })

      describe('when offer has been manually created', () => {
        it('should be able to edit price field', async () => {
          // given
          await renderStocks(props, store)
          fireEvent.click(screen.getByAltText('Modifier le stock'))

          // when
          fireEvent.change(screen.getByDisplayValue('10.01'), { target: { value: '127.03' } })

          // then
          expect(screen.queryByDisplayValue('10.01')).not.toBeInTheDocument()
          expect(screen.getByDisplayValue('127.03')).toBeInTheDocument()
        })

        it('should be able to edit booking limit date field', async () => {
          // given
          await renderStocks(props, store)
          fireEvent.click(screen.getByAltText('Modifier le stock'))

          // when
          fireEvent.click(screen.getByDisplayValue('18/12/2020'))
          fireEvent.click(screen.getByLabelText('day-17'))

          // then
          expect(screen.queryByDisplayValue('18/12/2020')).not.toBeInTheDocument()
          expect(screen.getByDisplayValue('17/12/2020')).toBeInTheDocument()
        })

        it('should be able to edit total quantity field', async () => {
          // given
          await renderStocks(props, store)
          fireEvent.click(screen.getByAltText('Modifier le stock'))

          // when
          fireEvent.change(screen.getByDisplayValue('10'), { target: { value: '23' } })

          // then
          expect(screen.queryByDisplayValue('10')).not.toBeInTheDocument()
          expect(screen.getByDisplayValue('23')).toBeInTheDocument()
        })

        it('should compute remaining quantity based on inputted total quantity', async () => {
          // given
          await renderStocks(props, store)
          fireEvent.click(screen.getByAltText('Modifier le stock'))

          // when
          fireEvent.change(screen.getByDisplayValue('10'), { target: { value: '9' } })

          // then
          const initialRemainingQuantity = screen.queryByText('6')
          expect(initialRemainingQuantity).not.toBeInTheDocument()

          const computedRemainingQuantity = screen.queryByText('5')
          expect(computedRemainingQuantity).toBeInTheDocument()
        })

        it('should set remaining quantity to Illimité when emptying total quantity field', async () => {
          // given
          await renderStocks(props, store)
          fireEvent.click(screen.getByAltText('Modifier le stock'))

          // when
          fireEvent.change(screen.getByDisplayValue('10'), { target: { value: '' } })

          // then
          const computedRemainingQuantity = screen.getByText('Illimité')
          expect(computedRemainingQuantity).toBeInTheDocument()
        })

        it('should not set remaining quantity to Illimité when total quantity is zero', async () => {
          // given
          pcapi.loadOffer.mockResolvedValue({
            ...thingOffer,
            stocks: [{ ...defaultStock, quantity: 0, bookingsQuantity: 0 }],
          })

          // when
          await renderStocks(props, store)

          // then
          expect(screen.getByLabelText('Quantité').value).not.toBe('')
          expect(screen.getByLabelText('Quantité').value).toBe('0')
          const remainingQuantityValue = screen.getAllByRole('cell')[3].textContent
          expect(remainingQuantityValue).not.toBe('Illimité')
          expect(remainingQuantityValue).toBe('0')
        })

        it('should display a validation button instead of an edition button', async () => {
          // given
          await renderStocks(props, store)

          // when
          fireEvent.click(screen.getByAltText('Modifier le stock'))

          // then
          expect(screen.getByAltText('Valider les modifications')).toBeInTheDocument()
          expect(screen.queryByAltText('Modifier le stock')).not.toBeInTheDocument()
        })

        it('should display a cancellation button instead of a deletion button', async () => {
          // given
          await renderStocks(props, store)

          // when
          fireEvent.click(screen.getByAltText('Modifier le stock'))

          // then
          expect(screen.getByAltText('Annuler les modifications')).toBeInTheDocument()
          expect(screen.queryByAltText('Supprimer le stock')).not.toBeInTheDocument()
        })

        it('should discard changes on stock when clicking on cancel button', async () => {
          // Given
          await renderStocks(props, store)
          fireEvent.click(screen.getByAltText('Modifier le stock'))

          fireEvent.change(screen.getByLabelText('Prix'), { target: { value: '14.01' } })

          fireEvent.click(screen.getByLabelText('Date limite de réservation'))
          fireEvent.click(screen.getByLabelText('day-25'))

          fireEvent.change(screen.getByLabelText('Quantité'), { target: { value: '6' } })

          // When
          fireEvent.click(screen.getByAltText('Annuler les modifications'))

          // Then
          expect(pcapi.updateStock).not.toHaveBeenCalled()
          expect(screen.getByLabelText('Prix').value).toBe('10.01')
          expect(screen.getByLabelText('Date limite de réservation').value).toBe('18/12/2020')
          expect(screen.getByLabelText('Quantité').value).toBe('10')
        })

        it('should exit edition mode on discard changes', async () => {
          // Given
          await renderStocks(props, store)
          fireEvent.click(screen.getByAltText('Modifier le stock'))

          // When
          fireEvent.click(screen.getByAltText('Annuler les modifications'))

          // Then
          expect(screen.queryByAltText('Valider les modifications')).not.toBeInTheDocument()
          expect(screen.queryByAltText('Annuler les modifications')).not.toBeInTheDocument()
        })

        describe('when clicking on validate button', () => {
          it('should save changes done to stock', async () => {
            // Given
            pcapi.updateStock.mockResolvedValue({})
            await renderStocks(props, store)
            fireEvent.click(screen.getByAltText('Modifier le stock'))

            fireEvent.change(screen.getByLabelText('Prix'), { target: { value: '14.01' } })

            fireEvent.click(screen.getByLabelText('Date limite de réservation'))
            fireEvent.click(screen.getByLabelText('day-25'))

            fireEvent.change(screen.getByLabelText('Quantité'), { target: { value: '6' } })

            // When
            fireEvent.click(screen.getByAltText('Valider les modifications'))

            // Then
            expect(pcapi.updateStock).toHaveBeenCalledWith({
              bookingLimitDatetime: '2020-12-25T23:59:59Z',
              id: '2E',
              price: '14.01',
              quantity: '6',
            })
            expect(screen.getByLabelText('Prix').value).toBe('14.01')
            expect(screen.getByLabelText('Date limite de réservation').value).toBe('25/12/2020')
            expect(screen.getByLabelText('Quantité').value).toBe('6')
          })

          it('should refresh offer and leave edition mode', async () => {
            // Given
            pcapi.updateStock.mockResolvedValue({})
            const initialOffer = {
              ...defaultOffer,
              stocks: [
                {
                  ...defaultStock,
                  price: 10.01,
                },
              ],
            }
            const updatedOffer = {
              ...defaultOffer,
              stocks: [
                {
                  ...defaultStock,
                  price: 10,
                },
              ],
            }
            pcapi.loadOffer.mockResolvedValueOnce(initialOffer).mockResolvedValueOnce(updatedOffer)
            await renderStocks(props, store)
            fireEvent.click(screen.getByAltText('Modifier le stock'))

            // When
            await act(async () => {
              await fireEvent.click(screen.getByAltText('Valider les modifications'))
            })

            // Then
            expect(pcapi.loadOffer).toHaveBeenCalledTimes(2)
            expect(screen.queryByAltText('Valider les modifications')).not.toBeInTheDocument()
            expect(screen.queryByAltText('Annuler les modifications')).not.toBeInTheDocument()
          })

          it('should set booking limit time to end of selected day when specified', async () => {
            // Given
            pcapi.updateStock.mockResolvedValue({})
            await renderStocks(props, store)
            fireEvent.click(screen.getByAltText('Modifier le stock'))
            fireEvent.click(screen.getByLabelText('Date limite de réservation'))
            fireEvent.click(screen.getByLabelText('day-19'))

            // When
            fireEvent.click(screen.getByAltText('Valider les modifications'))
            // Then
            expect(pcapi.updateStock.mock.calls[0][0].bookingLimitDatetime).toBe(
              '2020-12-19T23:59:59Z'
            )
          })

          it('should set booking limit datetime to null when not specified', async () => {
            // Given
            pcapi.updateStock.mockResolvedValue({})
            await renderStocks(props, store)
            fireEvent.click(screen.getByAltText('Modifier le stock'))
            fireEvent.change(screen.getByLabelText('Date limite de réservation'), {
              target: { value: '' },
            })

            // When
            fireEvent.click(screen.getByAltText('Valider les modifications'))

            // Then
            expect(pcapi.updateStock.mock.calls[0][0].bookingLimitDatetime).toBeNull()
          })

          it('should set price to 0 when not specified', async () => {
            // Given
            pcapi.updateStock.mockResolvedValue({})
            await renderStocks(props, store)
            fireEvent.click(screen.getByAltText('Modifier le stock'))
            fireEvent.change(screen.getByLabelText('Prix'), { target: { value: '' } })

            // When
            fireEvent.click(screen.getByAltText('Valider les modifications'))
            // Then
            expect(pcapi.updateStock.mock.calls[0][0].price).toBe(0)
          })

          it('should set quantity to null when not specified', async () => {
            // Given
            pcapi.updateStock.mockResolvedValue({})
            await renderStocks(props, store)
            fireEvent.click(screen.getByAltText('Modifier le stock'))
            fireEvent.change(screen.getByLabelText('Quantité'), { target: { value: '' } })

            // When
            fireEvent.click(screen.getByAltText('Valider les modifications'))
            // Then
            expect(pcapi.updateStock.mock.calls[0][0].quantity).toBeNull()
          })
        })
      })

      describe('when offer has been synchronized (with Titelive, leslibraires.fr, FNAC or Praxiel)', () => {
        beforeEach(() => {
          const synchronisedThingOffer = {
            ...thingOffer,
            lastProviderId: 'D4',
          }
          pcapi.loadOffer.mockResolvedValue(synchronisedThingOffer)
        })

        afterEach(() => {
          pcapi.loadOffer.mockReset()
        })

        it('should not be able to edit a stock', async () => {
          // Given
          await renderStocks(props, store)
          const editStockButton = screen.getByAltText('Modifier le stock').closest('button')

          // When
          fireEvent.click(editStockButton)

          // Then
          expect(editStockButton).toBeDisabled()
          expect(screen.getByLabelText('Prix')).toBeDisabled()
          expect(screen.getByLabelText('Date limite de réservation')).toBeDisabled()
          expect(screen.getByLabelText('Quantité')).toBeDisabled()
        })

        it('should not be able to delete a stock', async () => {
          // When
          await renderStocks(props, store)

          // Then
          expect(screen.getByAltText('Supprimer le stock').closest('button')).toBeDisabled()
        })
      })
    })
  })
})
