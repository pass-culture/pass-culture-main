import '@testing-library/jest-dom'

import { fireEvent, render, screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import React from 'react'
import { Provider } from 'react-redux'
import { MemoryRouter, Route } from 'react-router'

import { api } from 'apiClient/api'
import NotificationContainer from 'components/layout/Notification/NotificationContainer'
import OfferLayout from 'components/pages/Offers/Offer/OfferLayout'
import * as pcapi from 'repository/pcapi/pcapi'
import { configureTestStore } from 'store/testUtils'
import { queryByTextTrimHtml } from 'utils/testHelpers'

const GUYANA_CAYENNE_DEPT = '973'

jest.mock('repository/pcapi/pcapi', () => ({
  deleteStock: jest.fn(),
  loadCategories: jest.fn(),
  loadStocks: jest.fn(),
  bulkCreateOrEditStock: jest.fn(),
}))

jest.mock('utils/date', () => ({
  ...jest.requireActual('utils/date'),
  getToday: jest
    .fn()
    .mockImplementation(() => new Date('2020-12-15T12:00:00Z')),
}))

const renderOffers = async (
  props,
  storeOverrides,
  pathname = '/offre/AG3A/individuel/stocks'
) => {
  const store = configureTestStore(storeOverrides)
  return render(
    <Provider store={store}>
      <MemoryRouter initialEntries={[{ pathname: pathname }]}>
        <Route path="/offre/:offerId([A-Z0-9]+)/individuel">
          {() => <OfferLayout {...props} />}
        </Route>
      </MemoryRouter>
      <NotificationContainer />
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
      status: 'DRAFT',
      stocks: [],
      dateCreated: '',
      dateRange: [],
      fieldsUpdated: [],
      hasBookingLimitDatetimesPassed: true,
      isActive: true,
      isBookable: true,
      isDigital: true,
      isDuo: true,
      isEditable: true,
      isEducational: false,
      isNational: true,
      isThing: true,
      mediaUrls: [],
      mediations: [],
      name: 'offer name',
      nonHumanizedId: 1,
      product: {
        fieldsUpdated: [],
        id: 'product_id',
        isGcuCompatible: true,
        isNational: false,
        mediaUrls: [],
        name: 'product name',
        thumbCount: 0,
      },
      productId: 'product_id',
      subcategoryId: 'CONFERENCE',
      venueId: 'BC',
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
    pcapi.loadStocks.mockResolvedValue({ stocks: [] })
    pcapi.loadCategories.mockResolvedValue({
      categories: [],
      subcategories: [],
    })
    pcapi.deleteStock.mockResolvedValue({ id: stockId })
    pcapi.bulkCreateOrEditStock.mockResolvedValue({})
    jest.spyOn(api, 'listOfferersNames').mockResolvedValue([
      {
        id: 'AB',
        name: 'offerer name',
      },
    ])
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

  describe('create', () => {
    it('should not display offer status', async () => {
      // Given / When
      await renderOffers(props, store)
      await screen.findByRole('heading', { name: 'Stocks et prix' })

      // Then
      expect(screen.queryByText('brouillon')).not.toBeInTheDocument()
    })

    it('should redirect to summary page after submitting stock', async () => {
      // Given
      pcapi.bulkCreateOrEditStock.mockResolvedValue({})

      await renderOffers(props, store)

      await userEvent.click(await screen.findByText('Ajouter un stock'))
      fireEvent.change(screen.getByLabelText('Prix'), {
        target: { value: '15' },
      })

      // When
      await userEvent.click(screen.getByText('Étape suivante'))

      // Then
      const summaryPage = await screen.findByText('Vous y êtes presque !')
      expect(summaryPage).toBeInTheDocument()
    })

    describe('event offer', () => {
      let noStockOffer
      beforeEach(() => {
        noStockOffer = {
          ...defaultOffer,
          isEvent: true,
          stocks: [],
        }

        jest.spyOn(api, 'getOffer').mockResolvedValue(noStockOffer)
      })

      it('should not display remaining stocks and bookings columns when no stocks yet', async () => {
        // given
        await renderOffers(props, store)

        // when
        await userEvent.click(await screen.findByText('Ajouter une date'))

        // then
        expect(screen.queryByText('Stock restant')).not.toBeInTheDocument()
        expect(screen.queryByText('Réservations')).not.toBeInTheDocument()
      })

      it('should cancel new stock addition when clicking on cancel button', async () => {
        // Given
        await renderOffers(props, store)
        await userEvent.click(await screen.findByText('Ajouter une date'))

        // When
        await userEvent.click(screen.getByTitle('Opérations sur le stock'))

        await userEvent.click(screen.getByTitle('Supprimer le stock'))

        // Then
        expect(pcapi.bulkCreateOrEditStock).not.toHaveBeenCalled()
        expect(screen.queryByRole('row')).not.toBeInTheDocument()
      })

      it('should append new stock line on top of stocks list when clicking on add button', async () => {
        // given
        const eventStock = {
          ...defaultStock,
          beginningDatetime: '2020-12-20T22:00:00Z',
        }
        pcapi.loadStocks.mockResolvedValue({ stocks: [eventStock] })
        await renderOffers(props, store)
        await userEvent.click(await screen.findByText('Ajouter une date'))

        // when
        await userEvent.click(screen.getByText('Ajouter une date'))

        // then
        expect(screen.getAllByRole('row')).toHaveLength(4)
        const eventsDates = screen.getAllByLabelText('Date de l’évènement')
        expect(eventsDates[0].value).toBe('')
        expect(eventsDates[1].value).toBe('')
        expect(eventsDates[2].value).toBe('20/12/2020')
      })

      it('should have date, hour, price, limit datetime and quantity fields emptied by default', async () => {
        // given
        await renderOffers(props, store)

        // when
        await userEvent.click(await screen.findByText('Ajouter une date'))

        // then
        expect(screen.getByLabelText('Date de l’évènement').value).toBe('')
        expect(screen.getByLabelText('Heure de l’évènement').value).toBe('')
        expect(screen.getByLabelText('Prix').value).toBe('')
        expect(screen.getByLabelText('Date limite de réservation').value).toBe(
          ''
        )
        expect(screen.getByLabelText('Quantité').value).toBe('')
      })

      it('should not have remaining stocks and bookings columns', async () => {
        // given
        await renderOffers(props, store)

        // when
        await userEvent.click(await screen.findByText('Ajouter une date'))

        // then
        const columnCells = screen.getAllByRole('cell')
        expect(columnCells[3].textContent).toBe('')
        expect(columnCells[4].textContent).toBe('')
      })

      it('should have a cancel button to cancel new stock', async () => {
        // given
        await renderOffers(props, store)

        // when
        await userEvent.click(await screen.findByText('Ajouter une date'))

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
            activationCodes: [],
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
            activationCodes: [],
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

        await userEvent.click(await screen.findByText('Ajouter une date'))

        await userEvent.click(
          screen.getAllByLabelText('Date de l’évènement')[0]
        )
        await userEvent.click(screen.getByText('24'))

        await userEvent.click(
          screen.getAllByLabelText('Heure de l’évènement')[0]
        )
        await userEvent.click(screen.getByText('20:00'))

        fireEvent.change(screen.getByLabelText('Prix'), {
          target: { value: '15' },
        })

        await userEvent.click(
          screen.getAllByLabelText('Date limite de réservation')[0]
        )
        await userEvent.click(screen.getByText('22'))

        fireEvent.change(screen.getByLabelText('Quantité'), {
          target: { value: '15' },
        })

        await userEvent.click(screen.getByText('Ajouter une date'))

        await userEvent.click(
          screen.getAllByLabelText('Date de l’évènement')[0]
        )
        await userEvent.click(screen.getByText('25'))

        await userEvent.click(
          screen.getAllByLabelText('Heure de l’évènement')[0]
        )
        await userEvent.click(screen.getByText('20:00'))

        fireEvent.change(screen.getAllByLabelText('Prix')[0], {
          target: { value: '0' },
        })

        await userEvent.click(
          screen.getAllByLabelText('Date limite de réservation')[0]
        )
        await userEvent.click(screen.getByText('23'))

        // when
        await userEvent.click(screen.getByText('Étape suivante'))

        // then
        expect(pcapi.bulkCreateOrEditStock).toHaveBeenCalledWith(
          defaultOffer.id,
          [
            {
              beginningDatetime: '2020-12-25T23:00:00Z',
              bookingLimitDatetime: '2020-12-24T02:59:59Z',
              price: '0',
              quantity: null,
            },
            {
              beginningDatetime: '2020-12-24T23:00:00Z',
              bookingLimitDatetime: '2020-12-23T02:59:59Z',
              price: '15',
              quantity: '15',
            },
          ]
        )
      })

      it('should be able to add second stock while first one is not validated', async () => {
        // Given
        await renderOffers(props, store)

        // When
        await userEvent.click(await screen.findByText('Ajouter une date'))

        // Then
        expect(screen.getByText('Ajouter une date')).toBeEnabled()
      })

      it('should not display price error when the price is above 300 euros and offer is not educational', async () => {
        // Given
        await renderOffers(props, store)
        await userEvent.click(await screen.findByText('Ajouter une date'))

        await userEvent.click(screen.getByLabelText('Date de l’évènement'))
        await userEvent.click(screen.getByText('24'))

        await userEvent.click(screen.getByLabelText('Heure de l’évènement'))
        await userEvent.click(screen.getByText('20:00'))

        // When
        fireEvent.change(screen.getByLabelText('Prix'), {
          target: { value: '301' },
        })
        await userEvent.click(screen.getByText('Étape suivante'))

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

      it('should display error message on api error', async () => {
        // Given
        pcapi.bulkCreateOrEditStock.mockRejectedValueOnce({
          errors: {
            price: 'Le prix est invalide.',
            quantity: 'La quantité est invalide.',
          },
        })
        await renderOffers(props, store)
        await userEvent.click(await screen.findByText('Ajouter une date'))

        await userEvent.click(screen.getByLabelText('Date de l’évènement'))
        await userEvent.click(screen.getByText('26'))

        await userEvent.click(screen.getByLabelText('Heure de l’évènement'))
        await userEvent.click(screen.getByText('20:00'))

        fireEvent.change(screen.getByLabelText('Prix'), {
          target: { value: '10' },
        })

        // When
        await userEvent.click(screen.getByText('Étape suivante'))

        // Then
        const errorMessage = await screen.findByText(
          'Une ou plusieurs erreurs sont présentes dans le formulaire.'
        )
        expect(errorMessage).toBeInTheDocument()
      })

      it('should display error message on pre-submit error', async () => {
        // Given
        await renderOffers(props, store)
        await userEvent.click(await screen.findByText('Ajouter une date'))

        await userEvent.click(screen.getByLabelText('Date de l’évènement'))
        await userEvent.click(screen.getByText('26'))

        await userEvent.click(screen.getByLabelText('Heure de l’évènement'))
        await userEvent.click(screen.getByText('20:00'))

        fireEvent.change(screen.getByLabelText('Prix'), {
          target: { value: '-10' },
        })
        fireEvent.change(screen.getByLabelText('Quantité'), {
          target: { value: '-20' },
        })

        // When
        await userEvent.click(screen.getByText('Étape suivante'))

        // Then
        const errorMessage = await screen.findByText(
          'Une ou plusieurs erreurs sont présentes dans le formulaire.'
        )
        expect(errorMessage).toBeInTheDocument()
        expect(screen.getByLabelText('Prix')).toHaveClass('error')
        expect(screen.getByLabelText('Quantité')).toHaveClass('error')
        expect(pcapi.bulkCreateOrEditStock).toHaveBeenCalledTimes(0)
      })

      it('should redirect to summary page after submitting stock', async () => {
        // Given
        pcapi.bulkCreateOrEditStock.mockResolvedValueOnce({})
        await renderOffers(props, store)
        await userEvent.click(await screen.findByText('Ajouter une date'))

        await userEvent.click(screen.getByLabelText('Date de l’évènement'))
        await userEvent.click(screen.getByText('26'))

        await userEvent.click(screen.getByLabelText('Heure de l’évènement'))
        await userEvent.click(screen.getByText('20:00'))

        fireEvent.change(screen.getByLabelText('Prix'), {
          target: { value: '10' },
        })

        // When
        await userEvent.click(screen.getByText('Étape suivante'))

        // Then
        const summaryPage = await screen.findByText('Vous y êtes presque !')
        expect(summaryPage).toBeInTheDocument()
      })
    })

    describe('thing offer', () => {
      let noStockOffer
      beforeEach(() => {
        noStockOffer = {
          ...defaultOffer,
          isEvent: false,
          isThing: true,
          isDigital: false,
          stocks: [],
        }
        jest.spyOn(api, 'getOffer').mockResolvedValue(noStockOffer)
      })

      it('should not display add activation codes option when not digital', async () => {
        // given
        await renderOffers(props, store)

        // when
        await userEvent.click(await screen.findByText('Ajouter un stock'))

        // then
        expect(
          screen.queryByText('Ajouter des codes d’activation')
        ).not.toBeInTheDocument()
      })

      it('should display price error when the price is above 300 euros and offer is not educational', async () => {
        // Given
        await renderOffers(props, store)

        await userEvent.click(await screen.findByText('Ajouter un stock'))
        fireEvent.change(screen.getByLabelText('Prix'), {
          target: { value: '301' },
        })

        // When
        await userEvent.click(screen.getByText('Étape suivante'))

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
        pcapi.bulkCreateOrEditStock.mockRejectedValue({
          errors: {
            price: 'Le prix est invalide.',
            quantity: 'La quantité est invalide.',
          },
        })
        await renderOffers(props, store)
        await userEvent.click(await screen.findByText('Ajouter un stock'))

        fireEvent.change(screen.getByLabelText('Quantité'), {
          target: { value: '15' },
        })

        // When
        await userEvent.click(screen.getByText('Étape suivante'))

        // Then
        const errorMessage = await screen.findByText(
          'Une ou plusieurs erreurs sont présentes dans le formulaire.'
        )
        expect(errorMessage).toBeInTheDocument()
      })

      it('should display error message on pre-submit error', async () => {
        // Given
        await renderOffers(props, store)
        await userEvent.click(await screen.findByText('Ajouter un stock'))

        fireEvent.change(screen.getByLabelText('Prix'), {
          target: { value: '-10' },
        })
        fireEvent.change(screen.getByLabelText('Quantité'), {
          target: { value: '-20' },
        })

        // When
        await userEvent.click(screen.getByText('Étape suivante'))

        // Then
        const errorMessage = await screen.findByText(
          'Une ou plusieurs erreurs sont présentes dans le formulaire.'
        )
        expect(errorMessage).toBeInTheDocument()
        expect(screen.getByLabelText('Prix')).toHaveClass('error')
        expect(screen.getByLabelText('Quantité')).toHaveClass('error')
        expect(pcapi.bulkCreateOrEditStock).toHaveBeenCalledTimes(0)
      })

      it('should redirect to summary page after submitting stock', async () => {
        // Given
        pcapi.bulkCreateOrEditStock.mockResolvedValue({})
        await renderOffers(props, store)
        await userEvent.click(await screen.findByText('Ajouter un stock'))

        fireEvent.change(screen.getByLabelText('Prix'), {
          target: { value: '15' },
        })
        fireEvent.change(screen.getByLabelText('Quantité'), {
          target: { value: '15' },
        })

        // When
        await userEvent.click(screen.getByText('Étape suivante'))

        // Then
        const summaryPage = await screen.findByText('Vous y êtes presque !')
        expect(summaryPage).toBeInTheDocument()
      })

      it('should cancel new stock addition when clicking on cancel button', async () => {
        // Given
        await renderOffers(props, store)
        await userEvent.click(await screen.findByText('Ajouter un stock'))

        // When
        await userEvent.click(screen.getByTitle('Supprimer le stock'))

        // Then
        expect(pcapi.bulkCreateOrEditStock).not.toHaveBeenCalled()
        expect(screen.queryByRole('row')).not.toBeInTheDocument()
      })

      it('should not display remaining stocks and bookings columns when no stocks yet', async () => {
        // given
        const thingOffer = {
          ...defaultOffer,
          isEvent: false,
          stocks: [],
        }
        jest.spyOn(api, 'getOffer').mockResolvedValue(thingOffer)
        await renderOffers(props, store)

        // when
        await userEvent.click(await screen.findByText('Ajouter un stock'))

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
        jest.spyOn(api, 'getOffer').mockResolvedValue(thingOffer)
        await renderOffers(props, store)

        // when
        await userEvent.click(await screen.findByText('Ajouter un stock'))

        // then
        expect(screen.getAllByRole('row')).toHaveLength(2)
      })

      it('should have price, limit datetime and quantity fields emptied by default', async () => {
        // given
        await renderOffers(props, store)

        // when
        await userEvent.click(await screen.findByText('Ajouter un stock'))

        // then
        expect(screen.getByLabelText('Prix').value).toBe('')
        expect(screen.getByLabelText('Date limite de réservation').value).toBe(
          ''
        )
        expect(screen.getByLabelText('Quantité').value).toBe('')
      })

      it('should not have remaining stocks and bookings columns', async () => {
        // given
        await renderOffers(props, store)

        // when
        await userEvent.click(await screen.findByText('Ajouter un stock'))

        // then
        expect(screen.queryByText('Stock restant')).not.toBeInTheDocument()
        expect(screen.queryByText('Réservations')).not.toBeInTheDocument()
      })

      it('should have a cancel button to cancel new stock', async () => {
        // given
        await renderOffers(props, store)

        // when
        await userEvent.click(await screen.findByText('Ajouter un stock'))

        // then
        expect(screen.queryByTitle('Supprimer le stock')).toBeInTheDocument()
      })

      it('should add new stock to stocks and remove new empty stock line when clicking on validate button', async () => {
        // given
        pcapi.bulkCreateOrEditStock.mockResolvedValue({})
        await renderOffers(props, store)

        await userEvent.click(await screen.findByText('Ajouter un stock'))

        fireEvent.change(screen.getByLabelText('Prix'), {
          target: { value: '15' },
        })

        await userEvent.click(
          screen.getByLabelText('Date limite de réservation')
        )
        await userEvent.click(screen.getByText('22'))

        fireEvent.change(screen.getByLabelText('Quantité'), {
          target: { value: '15' },
        })

        // when
        await userEvent.click(screen.getByText('Étape suivante'))

        // then
        expect(pcapi.bulkCreateOrEditStock).toHaveBeenCalledWith('AG3A', [
          {
            bookingLimitDatetime: '2020-12-23T02:59:59Z',
            price: '15',
            quantity: '15',
          },
        ])
      })

      describe('digital offer', () => {
        let digitalOffer
        beforeEach(() => {
          digitalOffer = {
            ...defaultOffer,
            isDigital: true,
            isThing: true,
            isEvent: false,
            stocks: [],
          }

          jest.spyOn(api, 'getOffer').mockResolvedValue(digitalOffer)
        })

        it('should allow the user to add activation codes when offer is digital', async () => {
          // given
          await renderOffers(props, store)

          // when
          await userEvent.click(await screen.findByText('Ajouter un stock'))
          const activationCodeButton = screen
            .getByText('Ajouter des codes d’activation')
            .closest('div')
          await userEvent.click(activationCodeButton)

          // then
          expect(
            screen.getByLabelText(
              'Importer un fichier .csv depuis l’ordinateur'
            )
          ).toBeInTheDocument()
        })
        it('should not allow the user to add activation codes when offer is digital and is event', async () => {
          let eventOffer = {
            ...digitalOffer,
            isEvent: true,
          }
          jest.spyOn(api, 'getOffer').mockResolvedValue(eventOffer)
          // given
          await renderOffers(props, store)

          // when
          await userEvent.click(await screen.findByText('Ajouter une date'))

          // then
          expect(
            screen.queryByText('Ajouter des codes d’activation')
          ).not.toBeInTheDocument()
        })

        it('should display number of activation codes to be added', async () => {
          // Given
          await renderOffers(props, store)

          await userEvent.click(await screen.findByText('Ajouter un stock'))
          const activationCodeButton = screen
            .getByText('Ajouter des codes d’activation')
            .closest('div')
          await userEvent.click(activationCodeButton)
          const uploadButton = screen.getByLabelText(
            'Importer un fichier .csv depuis l’ordinateur'
          )
          const file = new File(['ABH\nJHB'], 'activation_codes.csv', {
            type: 'text/csv',
          })

          // When
          fireEvent.change(uploadButton, {
            target: {
              files: [file],
            },
          })

          // Then
          await expect(
            screen.findByText(
              'Vous êtes sur le point d’ajouter 2 codes d’activation.'
            )
          ).resolves.toBeInTheDocument()
        })

        it('should not change step when file is null', async () => {
          // Given
          await renderOffers(props, store)

          await userEvent.click(await screen.findByText('Ajouter un stock'))
          const activationCodeButton = screen
            .getByText('Ajouter des codes d’activation')
            .closest('div')
          await userEvent.click(activationCodeButton)
          const uploadButton = screen.getByLabelText(
            'Importer un fichier .csv depuis l’ordinateur'
          )

          // When
          fireEvent.change(uploadButton, {
            target: {
              files: [null],
            },
          })

          // Then
          await waitFor(() => {
            expect(
              screen.queryByText(
                'Vous êtes sur le point d’ajouter 2 codes d’activations.'
              )
            ).not.toBeInTheDocument()
            expect(
              screen.getByLabelText(
                'Importer un fichier .csv depuis l’ordinateur'
              )
            ).toBeInTheDocument()
          })
        })

        it('should allow user to go back', async () => {
          // Given
          await renderOffers(props, store)

          await userEvent.click(await screen.findByText('Ajouter un stock'))
          const activationCodeButton = screen
            .getByText('Ajouter des codes d’activation')
            .closest('div')
          await userEvent.click(activationCodeButton)
          const uploadButton = screen.getByLabelText(
            'Importer un fichier .csv depuis l’ordinateur'
          )
          const file = new File(['ABH\nJHB'], 'activation_codes.csv', {
            type: 'text/csv',
          })

          // When
          fireEvent.change(uploadButton, {
            target: {
              files: [file],
            },
          })

          await userEvent.click(await screen.findByText('Retour'))

          // Then
          expect(
            screen.getByLabelText(
              'Importer un fichier .csv depuis l’ordinateur'
            )
          ).toBeInTheDocument()
        })

        it('should save changes done to stock with activation codes and readjust bookingLimitDatetime according to activationCodesExpirationDatetime', async () => {
          // Given
          pcapi.bulkCreateOrEditStock.mockResolvedValue({})
          await renderOffers(props, store)

          await userEvent.click(await screen.findByText('Ajouter un stock'))
          const activationCodeButton = screen
            .getByText('Ajouter des codes d’activation')
            .closest('div')
          await userEvent.click(activationCodeButton)
          const uploadButton = screen.getByLabelText(
            'Importer un fichier .csv depuis l’ordinateur'
          )
          const file = new File(['ABH\nJHB'], 'activation_codes.csv', {
            type: 'text/csv',
          })

          // When
          fireEvent.change(uploadButton, {
            target: {
              files: [file],
            },
          })

          await userEvent.click(
            await screen.findByLabelText('Date limite de validité')
          )
          await userEvent.click(screen.getByText('25'))
          await userEvent.click(screen.getByText('Valider'))

          const priceField = screen.getByLabelText('Prix')
          fireEvent.change(priceField, { target: { value: null } })
          fireEvent.change(priceField, { target: { value: '14.01' } })

          await userEvent.click(screen.getByText('Étape suivante'))

          // Then
          expect(pcapi.bulkCreateOrEditStock).toHaveBeenCalledWith(
            defaultOffer.id,
            [
              {
                activationCodes: ['ABH', 'JHB'],
                activationCodesExpirationDatetime: '2020-12-26T02:59:59Z',
                bookingLimitDatetime: '2020-12-19T02:59:59Z',
                id: undefined,
                price: '14.01',
                quantity: 2,
              },
            ]
          )
        })

        it('should save changes done to stock with activation codes and no activationCodesExpirationDatetime', async () => {
          // Given
          pcapi.bulkCreateOrEditStock.mockResolvedValue({})
          await renderOffers(props, store)

          await userEvent.click(await screen.findByText('Ajouter un stock'))
          const activationCodeButton = screen
            .getByText('Ajouter des codes d’activation')
            .closest('div')
          await userEvent.click(activationCodeButton)
          const uploadButton = screen.getByLabelText(
            'Importer un fichier .csv depuis l’ordinateur'
          )
          const file = new File(['ABH\nJHB'], 'activation_codes.csv', {
            type: 'text/csv',
          })

          // When
          fireEvent.change(uploadButton, {
            target: {
              files: [file],
            },
          })

          await userEvent.click(await screen.findByText('Valider'))

          const priceField = screen.getByLabelText('Prix')
          fireEvent.change(priceField, { target: { value: null } })
          fireEvent.change(priceField, { target: { value: '14.01' } })

          await userEvent.click(screen.getByText('Étape suivante'))

          // Then
          expect(pcapi.bulkCreateOrEditStock).toHaveBeenCalledWith(
            defaultOffer.id,
            [
              {
                activationCodes: ['ABH', 'JHB'],
                activationCodesExpirationDatetime: null,
                bookingLimitDatetime: null,
                id: undefined,
                price: '14.01',
                quantity: 2,
              },
            ]
          )
        })

        it('should change stock quantity and disable activation codes button on upload', async () => {
          // Given
          await renderOffers(props, store)

          await userEvent.click(await screen.findByText('Ajouter un stock'))
          const activationCodeButton = screen
            .getByText('Ajouter des codes d’activation')
            .closest('div')
          await userEvent.click(activationCodeButton)
          const uploadButton = screen.getByLabelText(
            'Importer un fichier .csv depuis l’ordinateur'
          )
          const file = new File(['ABH\nJHB'], 'activation_codes.csv', {
            type: 'text/csv',
          })

          // When
          fireEvent.change(uploadButton, {
            target: {
              files: [file],
            },
          })
          await userEvent.click(await screen.findByText('Valider'))

          // Then
          expect(screen.getByLabelText('Quantité').value).toBe('2')
          expect(screen.getByLabelText('Quantité')).toBeDisabled()
          expect(
            screen.getByText('Ajouter des codes d’activation').closest('div')
          ).toHaveAttribute('aria-disabled', 'true')
          expect(screen.queryByText('Valider')).not.toBeInTheDocument()
        })

        it('should limit expiration datetime when booking limit datetime is set and vice versa', async () => {
          // Given
          await renderOffers(props, store)
          await userEvent.click(await screen.findByText('Ajouter un stock'))
          await userEvent.click(
            screen.getByLabelText('Date limite de réservation')
          )
          await userEvent.click(screen.getByText('18'))

          const activationCodeButton = screen
            .getByText('Ajouter des codes d’activation')
            .closest('div')
          await userEvent.click(activationCodeButton)
          const uploadButton = screen.getByLabelText(
            'Importer un fichier .csv depuis l’ordinateur'
          )
          const file = new File(['ABH\nJHB'], 'activation_codes.csv', {
            type: 'text/csv',
          })
          fireEvent.change(uploadButton, {
            target: {
              files: [file],
            },
          })

          await userEvent.click(
            await screen.findByLabelText('Date limite de validité')
          )

          await userEvent.click(screen.getByText('22'))
          expect(
            screen.queryByDisplayValue('22/12/2020')
          ).not.toBeInTheDocument()

          await userEvent.click(
            screen.getByLabelText('Date limite de validité')
          )
          await userEvent.click(screen.getByText('25'))
          expect(
            screen.getAllByDisplayValue('25/12/2020')[0]
          ).toBeInTheDocument()
          expect(
            screen.getAllByDisplayValue('25/12/2020')[1]
          ).toBeInTheDocument()

          // When
          await userEvent.click(screen.getByText('Valider'))

          // Then
          await userEvent.click(screen.getByDisplayValue('18/12/2020'))
          await userEvent.click(screen.getByText('19'))
          expect(
            screen.queryByDisplayValue('19/12/2020')
          ).not.toBeInTheDocument()
          expect(screen.queryByDisplayValue('18/12/2020')).toBeInTheDocument()

          expect(screen.getByLabelText('Quantité').value).toBe('2')
          expect(screen.getByLabelText('Quantité')).toBeDisabled()
          expect(
            screen.getByText('Ajouter des codes d’activation').closest('div')
          ).toHaveAttribute('aria-disabled', 'true')
          expect(screen.queryByText('Valider')).not.toBeInTheDocument()
          expect(screen.getByDisplayValue('25/12/2020')).toBeDisabled()
        })

        it('should set booking limit datetime on expiration datetime change', async () => {
          // Given
          await renderOffers(props, store)
          await userEvent.click(await screen.findByText('Ajouter un stock'))

          const activationCodeButton = screen
            .getByText('Ajouter des codes d’activation')
            .closest('div')
          await userEvent.click(activationCodeButton)
          const uploadButton = screen.getByLabelText(
            'Importer un fichier .csv depuis l’ordinateur'
          )
          const file = new File(['ABH\nJHB'], 'activation_codes.csv', {
            type: 'text/csv',
          })
          fireEvent.change(uploadButton, {
            target: {
              files: [file],
            },
          })

          await userEvent.click(
            await screen.findByLabelText('Date limite de validité')
          )
          await userEvent.click(screen.getByText('22'))

          // When
          await userEvent.click(screen.getByText('Valider'))

          // Then
          expect(
            screen.getByLabelText('Date limite de réservation')
          ).toHaveDisplayValue('15/12/2020')
          expect(
            screen.getByText('Date limite de validité')
          ).toBeInTheDocument()
        })

        it('should discard activation codes and expiration datetime and close modal on close button click', async () => {
          // Given
          await renderOffers(props, store)

          await userEvent.click(await screen.findByText('Ajouter un stock'))
          const activationCodeButton = screen
            .getByText('Ajouter des codes d’activation')
            .closest('div')
          await userEvent.click(activationCodeButton)
          const uploadButton = screen.getByLabelText(
            'Importer un fichier .csv depuis l’ordinateur'
          )
          const file = new File(['ABH\nJHB'], 'activation_codes.csv', {
            type: 'text/csv',
          })
          fireEvent.change(uploadButton, {
            target: {
              files: [file],
            },
          })

          await userEvent.click(
            await screen.findByLabelText('Date limite de validité')
          )
          await userEvent.click(screen.getByText('22'))

          // When
          await userEvent.click(screen.getByTitle('Fermer la modale'))

          // Then
          expect(
            screen.queryByDisplayValue('22/12/2020')
          ).not.toBeInTheDocument()
          expect(screen.getByLabelText('Quantité').value).toBe('')
          expect(screen.getByLabelText('Quantité')).not.toBeDisabled()
          expect(
            screen.getByText('Ajouter des codes d’activation').closest('div')
          ).not.toHaveAttribute('aria-disabled', 'true')
          expect(screen.queryByText('Valider')).not.toBeInTheDocument()
        })

        it('should not allow to set activation codes on an existing stock', async () => {
          // given
          pcapi.bulkCreateOrEditStock.mockResolvedValue({})
          const offer = {
            ...defaultOffer,
            isDigital: true,
          }

          jest.spyOn(api, 'getOffer').mockResolvedValue(offer)
          const createdStock = {
            hasActivationCodes: true,
            activationCodes: ['ABC'],
            activationCodesExpirationDatetime: '2020-12-26T23:59:59Z',
            quantity: 15,
            price: 15,
            remainingQuantity: 15,
            bookingsQuantity: 0,
            bookingLimitDatetime: '2020-12-22T23:59:59Z',
            id: stockId,
          }
          pcapi.loadStocks.mockResolvedValueOnce({ stocks: [createdStock] })

          // when
          await renderOffers(props, store)

          // then
          await expect(
            screen.findByText('Étape suivante')
          ).resolves.toBeInTheDocument()
          expect(screen.getByLabelText('Quantité').value).toBe('15')
          expect(screen.getByLabelText('Quantité')).toBeDisabled()
          expect(screen.getByLabelText('Prix').value).toBe('15')
          expect(
            screen.getByLabelText('Date limite de réservation').value
          ).toBe('22/12/2020')
          expect(screen.getByLabelText('Date limite de validité').value).toBe(
            '26/12/2020'
          )
          expect(
            screen.getByText('Ajouter des codes d’activation').closest('div')
          ).toHaveAttribute('aria-disabled', 'true')
        })
      })
    })
  })
})
