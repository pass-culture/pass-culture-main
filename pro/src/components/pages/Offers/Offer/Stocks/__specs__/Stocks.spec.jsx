import '@testing-library/jest-dom'

import * as pcapi from 'repository/pcapi/pcapi'

import { MemoryRouter, Route } from 'react-router'
import { bulkFakeApiCreateOrEditStock, loadFakeApiStocks } from 'utils/fakeApi'
import { fireEvent, render, screen, waitFor } from '@testing-library/react'
import { offerFactory, stockFactory } from 'utils/apiFactories'

import NotificationContainer from 'components/layout/Notification/NotificationContainer'
import OfferLayout from 'components/pages/Offers/Offer/OfferLayout'
import { Provider } from 'react-redux'
import React from 'react'
import { apiV1 } from 'api/api'
import { configureTestStore } from 'store/testUtils'
import { getToday } from 'utils/date'
import { queryByTextTrimHtml } from 'utils/testHelpers'
import userEvent from '@testing-library/user-event'

const GUYANA_CAYENNE_DEPT = '973'
const PARIS_FRANCE_DEPT = '75'

jest.mock('repository/pcapi/pcapi', () => ({
  deleteStock: jest.fn(),
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
          <>
            <OfferLayout {...props} />
            <NotificationContainer />
          </>
        </Route>
      </MemoryRouter>
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
      data: {
        users: [{ publicName: 'François', isAdmin: false }],
      },
      user: { initialized: true },
    }
    props = {}

    defaultOffer = {
      id: 'AG3A',
      venue: {
        departementCode: GUYANA_CAYENNE_DEPT,
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
    jest.spyOn(apiV1, 'getOffersGetOffer').mockResolvedValue(defaultOffer)
    pcapi.loadStocks.mockResolvedValue({ stocks: [] })
    pcapi.deleteStock.mockResolvedValue({ id: stockId })
    pcapi.bulkCreateOrEditStock.mockResolvedValue({})
  })

  describe('render', () => {
    describe('when no stocks yet', () => {
      it('should not display empty stock list', async () => {
        // given
        pcapi.loadStocks.mockResolvedValue({ stocks: [] })

        // when
        await renderOffers(props, store)

        // then
        expect(screen.queryByRole('table')).not.toBeInTheDocument()
      })

      it('should not display action buttons if offer already created', async () => {
        // given
        pcapi.loadStocks.mockResolvedValue({ stocks: [] })

        // when
        await renderOffers(props, store)

        // then
        expect(screen.queryByText('Annuler et quitter')).not.toBeInTheDocument()
        expect(screen.queryByText('Enregistrer')).not.toBeInTheDocument()
      })

      it('should display add stock button', async () => {
        // given
        pcapi.loadStocks.mockResolvedValue({ stocks: [] })

        // when
        await renderOffers(props, store)

        // then
        await expect(
          screen.findByText('Ajouter un stock')
        ).resolves.toBeInTheDocument()
      })
    })

    it('should load stocks on mount', async () => {
      // when
      await renderOffers(props, store)

      // then
      await waitFor(() => expect(pcapi.loadStocks).toHaveBeenCalledTimes(1))
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
      jest
        .spyOn(apiV1, 'getOffersGetOffer')
        .mockResolvedValue(offerWithMultipleStocks)
      pcapi.loadStocks.mockResolvedValue({ stocks })

      // when
      await renderOffers(props, store)

      // then
      const beginningDatetimeFields = await screen.findAllByLabelText(
        'Date de l’événement'
      )
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
      await expect(screen.findByText('Illimité')).resolves.toBeInTheDocument()
    })

    it('should have cancel link to go back to offer details', async () => {
      // given
      const offer = {
        ...defaultOffer,
        stocks: [],
      }

      jest.spyOn(apiV1, 'getOffersGetOffer').mockResolvedValue(offer)
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
      const cancelLink = await screen.findByRole('link', {
        name: 'Annuler et quitter',
      })
      expect(cancelLink).toBeInTheDocument()
      expect(cancelLink).toHaveAttribute(
        'href',
        '/offre/AG3A/individuel/edition'
      )
    })

    describe('when offer is being created (DRAFT status)', () => {
      beforeEach(() => {
        const draftOffer = {
          ...defaultOffer,
          status: 'DRAFT',
        }

        jest.spyOn(apiV1, 'getOffersGetOffer').mockResolvedValue(draftOffer)
      })

      describe('when no stock yet', () => {
        it('should display a disabled "Valider et créer l’offre" button', async () => {
          // Given
          pcapi.loadStocks.mockResolvedValue({ stocks: [] })

          // When
          await renderOffers(props, store)

          // Then
          expect(
            await screen.findByText('Valider et créer l’offre', {
              selector: 'button',
            })
          ).toBeDisabled()
        })
      })

      describe('when at least one stock', () => {
        it('should display a "Valider et créer l’offre" button', async () => {
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
          expect(
            await screen.findByText('Valider et créer l’offre', {
              selector: 'button',
            })
          ).toBeEnabled()
        })
      })
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
        jest.spyOn(apiV1, 'getOffersGetOffer').mockResolvedValue(offer)
        pcapi.loadStocks.mockResolvedValue(stocks)

        // when
        await renderOffers(props, store)

        // then
        expect(
          await screen.findByText(
            'Votre offre a été refusée car elle ne respecte pas les Conditions Générales d’Utilisation du pass. Un e-mail contenant les conditions d’éligibilité d’une offre a été envoyé à l’adresse e-mail attachée à votre compte.'
          )
        ).toBeInTheDocument()
        expect(screen.getByText('Ajouter une date')).toBeDisabled()
        expect(screen.getByLabelText('Date de l’événement')).toBeDisabled()
        expect(screen.getByLabelText('Heure de l’événement')).toBeDisabled()
        expect(screen.getByLabelText('Prix')).toBeDisabled()
        expect(
          screen.getByLabelText('Date limite de réservation')
        ).toBeDisabled()
        expect(screen.getByLabelText('Quantité')).toBeDisabled()
        expect(screen.getByTitle('Supprimer le stock')).toHaveAttribute(
          'aria-disabled',
          'true'
        )
        expect(screen.getByText('Enregistrer')).toBeDisabled()
      })

      it('should display status informative message and disable all fields when offer is pending for validation', async () => {
        // given
        offer.status = 'PENDING'
        offer.isActive = true
        jest.spyOn(apiV1, 'getOffersGetOffer').mockResolvedValue(offer)
        pcapi.loadStocks.mockResolvedValue(stocks)

        // when
        await renderOffers({}, store)

        // then
        expect(
          await screen.findByText(
            'Votre offre est en cours de validation par l’équipe du pass Culture. Une fois validée, vous recevrez un e-mail de confirmation et votre offre sera automatiquement mise en ligne.'
          )
        ).toBeInTheDocument()
        expect(screen.getByText('Ajouter une date')).toBeDisabled()
        expect(screen.getByLabelText('Date de l’événement')).toBeDisabled()
        expect(screen.getByLabelText('Heure de l’événement')).toBeDisabled()
        expect(screen.getByLabelText('Prix')).toBeDisabled()
        expect(
          screen.getByLabelText('Date limite de réservation')
        ).toBeDisabled()
        expect(screen.getByLabelText('Quantité')).toBeDisabled()
        expect(screen.getByTitle('Supprimer le stock')).toHaveAttribute(
          'aria-disabled',
          'true'
        )
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

        jest.spyOn(apiV1, 'getOffersGetOffer').mockResolvedValue(eventOffer)
        pcapi.loadStocks.mockResolvedValue({ stocks: [eventStock] })
      })

      it('should display an information message regarding booking cancellation', async () => {
        // when
        await renderOffers(props, store)

        // then
        const informationMessage = await screen.findByText(
          'Les utilisateurs ont un délai de 48h pour annuler leur réservation mais ne peuvent pas le faire moins de 48h avant le début de l’événement. Si la date limite de réservation n’est pas encore passée, la place est alors automatiquement remise en vente.'
        )
        expect(informationMessage).toBeInTheDocument()
      })

      it('should display button to add date', async () => {
        // when
        await renderOffers(props, store)

        // then
        const buttonAddDate = await screen.findByRole('button', {
          name: 'Ajouter une date',
        })
        expect(buttonAddDate).toBeInTheDocument()
      })

      it("should display offer's stocks fields", async () => {
        // when
        await renderOffers(props, store)

        // then
        expect(apiV1.getOffersGetOffer).toHaveBeenCalledWith('AG3A')

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

        expect(columnCells[7].querySelector('button').title).toBe(
          'Opérations sur le stock'
        )
      })
    })

    describe('render thing offer', () => {
      let thingOffer
      beforeEach(() => {
        thingOffer = {
          ...defaultOffer,
          isEvent: false,
        }
        jest.spyOn(apiV1, 'getOffersGetOffer').mockResolvedValue(thingOffer)
        pcapi.loadStocks.mockResolvedValue({ stocks: [{ ...defaultStock }] })
      })

      it('should display an information message regarding booking cancellation with 10 days auto expiry when subcategory is LIVRE_PAPIER', async () => {
        // given
        thingOffer.subcategoryId = 'LIVRE_PAPIER'
        jest.spyOn(apiV1, 'getOffersGetOffer').mockResolvedValue(thingOffer)

        // when
        await renderOffers(props, store)

        // then
        const informationMessage = await screen.findByText(
          'Les utilisateurs ont 10 jours pour faire valider leur contremarque. Passé ce délai, la réservation est automatiquement annulée et l’offre remise en vente.'
        )
        expect(informationMessage).toBeInTheDocument()
      })

      it('should display an information message regarding booking cancellation', async () => {
        // when
        await renderOffers(props, store)

        // then
        const informationMessage = await screen.findByText(
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
        expect(
          await screen.findByRole('button', { name: 'Ajouter un stock' })
        ).toBeEnabled()
      })

      it('should not be able to add a new stock if there is already one', async () => {
        // When
        await renderOffers(props, store)

        // Then
        expect(
          screen.queryByRole('button', { name: 'Ajouter un stock' })
        ).not.toBeInTheDocument()
      })

      it("should display offer's stock fields", async () => {
        // when
        await renderOffers(props, store)

        // then
        expect(apiV1.getOffersGetOffer).toHaveBeenCalledWith('AG3A')

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

        expect(columnCells[5].querySelector('button').title).toBe(
          'Opérations sur le stock'
        )
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
          jest
            .spyOn(apiV1, 'getOffersGetOffer')
            .mockResolvedValue(synchronisedThingOffer)
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
          expect(
            screen.queryByRole('button', { name: 'Ajouter un stock' })
          ).not.toBeInTheDocument()
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
        jest.spyOn(apiV1, 'getOffersGetOffer').mockResolvedValue(digitalOffer)
        pcapi.loadStocks.mockResolvedValue({ stocks: [{ ...defaultStock }] })
      })

      it('should display an information message regarding booking cancellation (when feature toggling)', async () => {
        store = configureTestStore({
          data: {
            users: [{ publicName: 'François', isAdmin: false }],
          },
        })

        // when
        await renderOffers(props, store)

        // then
        const informationMessage = await screen.findByText(
          'Les utilisateurs ont 30 jours pour annuler leurs réservations d’offres numériques. Dans le cas d’offres avec codes d’activation, les utilisateurs ne peuvent pas annuler leurs réservations d’offres numériques. Toute réservation est définitive et sera immédiatement validée.'
        )
        expect(informationMessage).toBeInTheDocument()
      })
    })

    describe('when the user clicks several time on the "Enregistrer" button', () => {
      it('should display a disabled "Enregistrer" button when no errors', async () => {
        // Given

        const stock = stockFactory()
        const offer = offerFactory({ id: 'AG3A', status: 'ACTIVE' })
        jest.spyOn(apiV1, 'getOffersGetOffer').mockResolvedValue(offer)
        loadFakeApiStocks([stock])
        // do not resolve promise so that button remains in disabled state
        jest
          .spyOn(pcapi, 'bulkCreateOrEditStock')
          .mockImplementation(() => new Promise(() => {}))
        await renderOffers(props, store)
        const submitButton = await screen.findByRole('button', {
          type: 'submit',
          name: 'Enregistrer',
        })

        // When
        await userEvent.click(submitButton)

        // Then
        expect(submitButton.firstChild).toBeEmptyDOMElement()
        expect(submitButton).toBeDisabled()
      })

      it('should display an enabled "Enregistrer" button after clicking on it when there is an error in the form', async () => {
        // Given
        let eventOffer = {
          ...defaultOffer,
          isEvent: true,
        }

        jest.spyOn(apiV1, 'getOffersGetOffer').mockResolvedValue(eventOffer)
        pcapi.loadStocks.mockResolvedValue({ stocks: [] })
        pcapi.bulkCreateOrEditStock.mockResolvedValue({})

        await renderOffers(props, store)

        await userEvent.click(await screen.findByText('Ajouter une date'))
        await userEvent.click(screen.getByLabelText('Date de l’événement'))
        await userEvent.click(screen.getByText('26'))
        await userEvent.click(screen.getByLabelText('Heure de l’événement'))
        await userEvent.click(screen.getByText('20:00'))
        const submitButton = screen.getByText('Enregistrer', {
          selector: 'button',
        })

        // When
        await userEvent.click(submitButton)

        // Then
        expect(submitButton).toBeEnabled()
      })
    })
  })

  describe('mandatory fields', () => {
    let eventOffer
    beforeEach(() => {
      eventOffer = {
        ...defaultOffer,
        isEvent: true,
      }

      jest.spyOn(apiV1, 'getOffersGetOffer').mockResolvedValue(eventOffer)
      pcapi.loadStocks.mockResolvedValue({ stocks: [] })
      pcapi.bulkCreateOrEditStock.mockResolvedValue({})
    })

    it('should have mandatory beginning date field for event offer', async () => {
      // Given
      await renderOffers(props, store)

      await userEvent.click(await screen.findByText('Ajouter une date'))

      await userEvent.click(screen.getByLabelText('Heure de l’événement'))
      await userEvent.click(screen.getByText('20:00'))

      fireEvent.change(screen.getByLabelText('Prix'), {
        target: { value: '10' },
      })

      // When
      await userEvent.click(screen.getByText('Enregistrer'))

      // Then
      const errorMessage = await screen.findByText(
        'Une ou plusieurs erreurs sont présentes dans le formulaire.'
      )
      expect(errorMessage).toBeInTheDocument()
    })

    it('should have mandatory beginning time field for event offer', async () => {
      // Given
      await renderOffers(props, store)

      await userEvent.click(await screen.findByText('Ajouter une date'))

      await userEvent.click(screen.getByLabelText('Date de l’événement'))
      await userEvent.click(screen.getByText('26'))

      fireEvent.change(screen.getByLabelText('Prix'), {
        target: { value: '10' },
      })

      // When
      await userEvent.click(screen.getByText('Enregistrer'))

      // Then
      const errorMessage = await screen.findByText(
        'Une ou plusieurs erreurs sont présentes dans le formulaire.'
      )
      expect(errorMessage).toBeInTheDocument()
    })

    it('should have mandatory price field', async () => {
      // Given
      await renderOffers(props, store)

      await userEvent.click(await screen.findByText('Ajouter une date'))

      await userEvent.click(screen.getByLabelText('Date de l’événement'))
      await userEvent.click(screen.getByText('26'))

      await userEvent.click(screen.getByLabelText('Heure de l’événement'))
      await userEvent.click(screen.getByText('20:00'))

      // When
      await userEvent.click(screen.getByText('Enregistrer'))

      // Then
      const errorMessage = await screen.findByText(
        'Une ou plusieurs erreurs sont présentes dans le formulaire.'
      )
      expect(errorMessage).toBeInTheDocument()
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
        .spyOn(apiV1, 'getOffersGetOffer')
        .mockResolvedValueOnce(initialOffer)
        .mockResolvedValueOnce(updatedOffer)
      pcapi.loadStocks
        .mockResolvedValueOnce({ stocks: [defaultStock] })
        .mockResolvedValueOnce({ stocks: [] })

      // When
      await renderOffers(props, store)

      // Then
      expect(await screen.findByText('active')).toBeInTheDocument()

      // When

      await userEvent.click(screen.getByTitle('Supprimer le stock'))
      await userEvent.click(
        await screen.findByText('Supprimer', { selector: 'button' })
      )

      // Then
      expect(screen.queryByText('épuisée')).toBeInTheDocument()
    })

    it('should stay on stocks page after validating of stocks', async () => {
      // Given
      const stock = stockFactory()
      const offer = offerFactory({ id: 'AG3A', status: 'ACTIVE' })
      jest.spyOn(apiV1, 'getOffersGetOffer').mockResolvedValue(offer)
      loadFakeApiStocks([stock])
      await renderOffers(props, store)

      // When
      await userEvent.click(
        await screen.findByText('Enregistrer', { selector: 'button' })
      )

      // Then
      expect(
        screen.getByText('Stock et prix', { selector: 'h3' })
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

        jest.spyOn(apiV1, 'getOffersGetOffer').mockResolvedValue(eventOffer)
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
          expect(await screen.findByLabelText('Prix')).toBeDisabled()
          expect(screen.getByLabelText('Date de l’événement')).toBeDisabled()
          expect(screen.getByLabelText('Heure de l’événement')).toBeDisabled()
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

          jest.spyOn(apiV1, 'getOffersGetOffer').mockResolvedValue(eventOffer)
          await renderOffers(props, store)

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

          pcapi.loadStocks.mockResolvedValue({ stocks: [eventInThePast] })
          await renderOffers(props, store)

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

          pcapi.loadStocks.mockResolvedValue({ stocks: [eventInThePast] })
          await renderOffers(props, store)

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

          pcapi.loadStocks.mockResolvedValue({ stocks: [eventInThePast] })
          await renderOffers(props, store)

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
            await renderOffers(props, store)

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
            await renderOffers(props, store)

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
            await renderOffers(props, store)

            // when
            fireEvent.change(
              await screen.findByLabelText('Date de l’événement'),
              {
                target: { value: null },
              }
            )

            // then
            expect(screen.getByLabelText('Date de l’événement')).toBeEnabled()
          })

          it('should be able to edit hour field', async () => {
            // given
            await renderOffers(props, store)

            // when
            await userEvent.click(await screen.findByDisplayValue('19:00'))
            await userEvent.click(screen.getByText('18:30'))

            // then
            expect(screen.queryByDisplayValue('19:00')).not.toBeInTheDocument()
            expect(screen.getByDisplayValue('18:30')).toBeInTheDocument()
          })

          it('should be able to edit price field', async () => {
            // given
            await renderOffers(props, store)
            const priceField = await screen.findByDisplayValue('10.01')

            // when
            fireEvent.change(priceField)
            fireEvent.change(priceField, { target: { value: '127.03' } })

            // then
            expect(screen.queryByDisplayValue('10.01')).not.toBeInTheDocument()
            expect(screen.getByDisplayValue('127.03')).toBeInTheDocument()
          })

          it('should be able to edit booking limit date field', async () => {
            // given
            await renderOffers(props, store)

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
            await renderOffers(props, store)

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
            await renderOffers(props, store)

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
            await renderOffers(props, store)
            const quantityField = await screen.findByDisplayValue('10')

            // when
            fireEvent.change(quantityField, { target: { value: null } })
            fireEvent.change(quantityField, { target: { value: '23' } })

            // then
            expect(screen.queryByDisplayValue('10')).not.toBeInTheDocument()
            expect(screen.getByDisplayValue('23')).toBeInTheDocument()
          })

          it('should not empty date field when emptying hour field', async () => {
            // given
            await renderOffers(props, store)

            // when
            fireEvent.change(await screen.findByDisplayValue('19:00'), {
              target: { value: null },
            })

            // then
            expect(screen.queryByDisplayValue('20/12/2020')).toBeInTheDocument()
          })

          it('should compute remaining quantity based on inputted total quantity', async () => {
            // given
            await renderOffers(props, store)
            const quantityField = await screen.findByDisplayValue('10')

            // when
            fireEvent.change(quantityField, { target: { value: null } })
            fireEvent.change(quantityField, { target: { value: '9' } })

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
            fireEvent.change(await screen.findByDisplayValue('10'), {
              target: { value: null },
            })

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
            expect(await screen.findByLabelText('Quantité')).toHaveValue(0)
            const remainingQuantityValue =
              screen.getAllByRole('cell')[5].textContent
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

              await userEvent.click(
                await screen.findByLabelText('Date de l’événement')
              )
              await userEvent.click(screen.getByText('26'))

              await userEvent.click(
                screen.getByLabelText('Heure de l’événement')
              )
              await userEvent.click(screen.getByText('20:00'))

              const priceField = screen.getByLabelText('Prix')
              fireEvent.change(priceField, { target: { value: null } })
              fireEvent.change(priceField, { target: { value: '14.01' } })

              await userEvent.click(
                screen.getByLabelText('Date limite de réservation')
              )
              await userEvent.click(screen.getByText('25'))

              const quantityField = screen.getByLabelText('Quantité')
              fireEvent.change(quantityField, { target: { value: null } })
              fireEvent.change(quantityField, { target: { value: '6' } })

              // When
              await userEvent.click(screen.getByText('Enregistrer'))

              // Then
              expect(pcapi.bulkCreateOrEditStock).toHaveBeenCalledWith(
                defaultOffer.id,
                [
                  {
                    beginningDatetime: '2020-12-26T23:00:00Z',
                    bookingLimitDatetime: '2020-12-26T02:59:59Z',
                    id: '2E',
                    price: '14.01',
                    quantity: '6',
                  },
                ]
              )
              expect(screen.getByLabelText('Date de l’événement').value).toBe(
                '26/12/2020'
              )
              expect(screen.getByLabelText('Heure de l’événement').value).toBe(
                '20:00'
              )
              expect(screen.getByLabelText('Prix').value).toBe('14.01')
              expect(
                screen.getByLabelText('Date limite de réservation').value
              ).toBe('25/12/2020')
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

              // When
              await userEvent.click(await screen.findByText('Enregistrer'))

              // Then
              expect(pcapi.loadStocks).toHaveBeenCalledTimes(2)
            })

            it('should set booking limit datetime to exact beginning datetime when not specified', async () => {
              // Given
              await renderOffers(props, store)
              fireEvent.change(
                await screen.findByLabelText('Date limite de réservation'),
                {
                  target: { value: '' },
                }
              )

              // When
              await userEvent.click(screen.getByText('Enregistrer'))

              // Then
              const savedStocks = pcapi.bulkCreateOrEditStock.mock.calls[0][1]
              expect(savedStocks[0].bookingLimitDatetime).toBe(
                '2020-12-20T22:00:00Z'
              )
            })

            it('should set booking limit datetime to exact beginning datetime when same as beginning date', async () => {
              // Given
              await renderOffers(props, store)
              await userEvent.click(
                await screen.findByLabelText('Date limite de réservation')
              )
              await userEvent.click(screen.getByText('20'))

              // When
              await userEvent.click(screen.getByText('Enregistrer'))

              // Then
              const savedStocks = pcapi.bulkCreateOrEditStock.mock.calls[0][1]
              expect(savedStocks[0].bookingLimitDatetime).toBe(
                '2020-12-20T22:00:00Z'
              )
            })

            it('should set booking limit time to end of selected locale day when specified and different than beginning date in Cayenne TZ', async () => {
              // Given
              await renderOffers(props, store)
              await userEvent.click(
                await screen.findByLabelText('Date limite de réservation')
              )
              await userEvent.click(screen.getByText('19'))

              // When
              await userEvent.click(screen.getByText('Enregistrer'))

              // Then
              const savedStocks = pcapi.bulkCreateOrEditStock.mock.calls[0][1]
              expect(savedStocks[0].bookingLimitDatetime).toBe(
                '2020-12-20T02:59:59Z'
              )
            })

            it('should set booking limit time to end of selected locale day when specified and different than beginning date in Paris TZ', async () => {
              // Given
              eventOffer.venue.departementCode = PARIS_FRANCE_DEPT

              await renderOffers(props, store)
              await userEvent.click(
                await screen.findByLabelText('Date limite de réservation')
              )
              await userEvent.click(screen.getByText('17'))

              // When
              await userEvent.click(screen.getByText('Enregistrer'))

              // Then
              const savedStocks = pcapi.bulkCreateOrEditStock.mock.calls[0][1]
              expect(savedStocks[0].bookingLimitDatetime).toBe(
                '2020-12-17T22:59:59Z'
              )
            })

            it('should set quantity to null when not specified', async () => {
              // Given
              await renderOffers(props, store)
              fireEvent.change(await screen.findByLabelText('Quantité'), {
                target: { value: null },
              })

              // When
              await userEvent.click(screen.getByText('Enregistrer'))

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

              await userEvent.click(
                await screen.findByLabelText('Date de l’événement')
              )
              await userEvent.click(screen.getByText('26'))

              await userEvent.click(
                screen.getByLabelText('Heure de l’événement')
              )
              await userEvent.click(screen.getByText('20:00'))

              // When
              await userEvent.click(screen.getByText('Enregistrer'))

              // Then
              const errorMessage = await screen.findByText(
                'Une ou plusieurs erreurs sont présentes dans le formulaire.'
              )
              expect(errorMessage).toBeInTheDocument()
            })

            it('should not be able to submit changes when beginning date field is empty', async () => {
              // given
              await renderOffers(props, store)
              const beginningDateField = await screen.findByDisplayValue(
                '20/12/2020'
              )
              fireEvent.change(beginningDateField, { target: { value: null } })

              // when
              await userEvent.click(screen.getByText('Enregistrer'))

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
              const beginningHourField = await screen.findByDisplayValue(
                '19:00'
              )
              fireEvent.change(beginningHourField, { target: { value: null } })

              // when
              await userEvent.click(screen.getByText('Enregistrer'))

              // then
              const errorMessage = await screen.findByText(
                'Une ou plusieurs erreurs sont présentes dans le formulaire.'
              )
              expect(errorMessage).toBeInTheDocument()
              expect(pcapi.bulkCreateOrEditStock).not.toHaveBeenCalled()
            })

            it('should not display price error when the price is above 300 euros and offer is not educational', async () => {
              // Given
              await renderOffers(props, store)
              fireEvent.change(await screen.findByLabelText('Prix'), {
                target: { value: '301' },
              })

              // When
              await userEvent.click(screen.getByText('Enregistrer'))

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
              pcapi.loadStocks.mockResolvedValue({ stocks: [eventStock] })
              pcapi.bulkCreateOrEditStock.mockResolvedValue({})

              await renderOffers(props, store)
              await userEvent.click(
                await screen.findByLabelText('Heure de l’événement')
              )
              await userEvent.click(screen.getByText('20:00'))

              // When
              await userEvent.click(screen.getByText('Enregistrer'))

              // Then
              const errorMessage = await screen.findByText(
                'Vos stocks ont bien été sauvegardés.'
              )
              expect(errorMessage).toBeInTheDocument()
            })

            it('should display error message on pre-submit error', async () => {
              // Given
              await renderOffers(props, store)

              await userEvent.click(
                await screen.findByLabelText('Date de l’événement')
              )
              await userEvent.click(screen.getByText('26'))

              await userEvent.click(
                screen.getByLabelText('Heure de l’événement')
              )
              await userEvent.click(screen.getByText('20:00'))

              fireEvent.change(screen.getByLabelText('Prix'), {
                target: { value: '-10' },
              })
              fireEvent.change(screen.getByLabelText('Quantité'), {
                target: { value: '-20' },
              })

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

              await userEvent.click(
                await screen.findByLabelText('Date de l’événement')
              )
              await userEvent.click(screen.getByText('26'))

              await userEvent.click(
                screen.getByLabelText('Heure de l’événement')
              )
              await userEvent.click(screen.getByText('20:00'))

              // When
              await userEvent.click(screen.getByText('Enregistrer'))

              // Then
              const errorMessage = await screen.findByText(
                'Vos stocks ont bien été sauvegardés.'
              )
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
              jest
                .spyOn(apiV1, 'getOffersGetOffer')
                .mockResolvedValueOnce(initialOffer)
                .mockResolvedValueOnce(updatedOffer)
              await renderOffers(props, store)
              apiV1.getOffersGetOffer.mockClear()

              // When
              await userEvent.click(await screen.findByText('Enregistrer'))

              // Then
              expect(apiV1.getOffersGetOffer).toHaveBeenCalledTimes(1)
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
              jest
                .spyOn(apiV1, 'getOffersGetOffer')
                .mockResolvedValueOnce(initialOffer)
                .mockResolvedValueOnce(updatedOffer)

              // When
              await renderOffers(props, store)

              // Then
              const soldOutOfferStatus = await screen.findByText('épuisée')
              expect(soldOutOfferStatus).toBeInTheDocument()

              await userEvent.click(screen.getByText('Enregistrer'))

              const successMessage = await screen.findByText(
                'Vos stocks ont bien été sauvegardés.'
              )
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
            await userEvent.click(
              await screen.findByTitle('Supprimer le stock')
            )

            // Then
            expect(
              screen.getByLabelText('Voulez-vous supprimer ce stock ?')
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
            expect(
              screen.getByRole('button', { name: 'Supprimer' })
            ).toHaveFocus()
          })

          it('should be able to delete a stock', async () => {
            // Given
            await renderOffers(props, store)

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
            await renderOffers(props, store)

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
            pcapi.loadStocks
              .mockResolvedValueOnce({ stocks: [initialStock] })
              .mockResolvedValueOnce({ stocks: [] })

            await renderOffers(props, store)

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
            pcapi.loadStocks
              .mockResolvedValueOnce({ stocks: [initialStock] })
              .mockResolvedValueOnce({ stocks: [] })
            jest.spyOn(apiV1, 'getOffersGetOffer').mockResolvedValue({
              ...defaultOffer,
              isEvent: true,
            })

            await renderOffers(props, store)
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
            await renderOffers(props, store)

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
            await renderOffers(props, store)

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
            await renderOffers(props, store)

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

          jest
            .spyOn(apiV1, 'getOffersGetOffer')
            .mockResolvedValue(eventOfferFromAllocine)
        })

        describe('when editing stock', () => {
          it('should be able to update price and quantity but not beginning date nor hour fields', async () => {
            // When
            await renderOffers(props, store)

            // Then
            expect(
              await screen.findByLabelText('Date de l’événement')
            ).toBeDisabled()
            expect(screen.getByLabelText('Heure de l’événement')).toBeDisabled()
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
        jest.spyOn(apiV1, 'getOffersGetOffer').mockResolvedValue(thingOffer)
        pcapi.loadStocks.mockResolvedValue({ stocks: [thingStock] })
      })

      describe('when offer has been manually created', () => {
        it('should be able to edit price field', async () => {
          // given
          await renderOffers(props, store)
          const priceField = await screen.findByDisplayValue('10.01')

          // when
          fireEvent.change(priceField)
          fireEvent.change(priceField, { target: { value: '127.03' } })

          // then
          expect(screen.queryByDisplayValue('10.01')).not.toBeInTheDocument()
          expect(screen.getByDisplayValue('127.03')).toBeInTheDocument()
        })

        it('should be able to edit booking limit date field', async () => {
          // given
          await renderOffers(props, store)

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
          await renderOffers(props, store)
          const quantityField = await screen.findByDisplayValue('10')

          // when
          fireEvent.change(quantityField, { target: { value: null } })
          fireEvent.change(quantityField, { target: { value: '23' } })

          // then
          expect(screen.queryByDisplayValue('10')).not.toBeInTheDocument()
          expect(screen.getByDisplayValue('23')).toBeInTheDocument()
        })

        it('should compute remaining quantity based on inputted total quantity', async () => {
          // given
          await renderOffers(props, store)
          const quantityField = await screen.findByDisplayValue('10')

          // when
          fireEvent.change(quantityField, { target: { value: null } })
          fireEvent.change(quantityField, { target: { value: '9' } })

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
          fireEvent.change(await screen.findByDisplayValue('10'), {
            target: { value: null },
          })

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
          expect(await screen.findByLabelText('Quantité')).toHaveValue(0)
          const remainingQuantityValue =
            screen.getAllByRole('cell')[3].textContent
          expect(remainingQuantityValue).toBe('0')
        })

        describe('when clicking on submit button', () => {
          it('should save changes done to stock', async () => {
            // Given
            pcapi.bulkCreateOrEditStock.mockResolvedValue({})
            await renderOffers(props, store)

            const priceField = await screen.findByLabelText('Prix')
            fireEvent.change(priceField, { target: { value: null } })
            fireEvent.change(priceField, { target: { value: '14.01' } })

            await userEvent.click(
              screen.getByLabelText('Date limite de réservation')
            )
            await userEvent.click(screen.getByText('25'))

            const quantityField = screen.getByLabelText('Quantité')
            fireEvent.change(quantityField, { target: { value: null } })
            fireEvent.change(quantityField, { target: { value: '6' } })

            // When
            await userEvent.click(screen.getByText('Enregistrer'))

            // Then
            expect(pcapi.bulkCreateOrEditStock).toHaveBeenCalledWith(
              defaultOffer.id,
              [
                {
                  bookingLimitDatetime: '2020-12-26T02:59:59Z',
                  id: '2E',
                  price: '14.01',
                  quantity: '6',
                },
              ]
            )
            expect(screen.getByLabelText('Prix').value).toBe('14.01')
            expect(
              screen.getByLabelText('Date limite de réservation').value
            ).toBe('25/12/2020')
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

            // When
            await userEvent.click(await screen.findByText('Enregistrer'))

            // Then
            expect(pcapi.loadStocks).toHaveBeenCalledTimes(2)
          })

          it('should set booking limit time to end of selected local day when specified in Cayenne TZ', async () => {
            // Given
            pcapi.bulkCreateOrEditStock.mockResolvedValue({})
            await renderOffers(props, store)
            await userEvent.click(
              await screen.findByLabelText('Date limite de réservation')
            )
            await userEvent.click(screen.getByText('19'))

            // When
            await userEvent.click(screen.getByText('Enregistrer'))

            // Then
            const savedStocks = pcapi.bulkCreateOrEditStock.mock.calls[0][1]
            expect(savedStocks[0].bookingLimitDatetime).toBe(
              '2020-12-20T02:59:59Z'
            )
          })

          it('should set booking limit time to end of selected local day when specified in Paris TZ', async () => {
            // Given
            thingOffer.venue.departementCode = PARIS_FRANCE_DEPT

            pcapi.bulkCreateOrEditStock.mockResolvedValue({})
            await renderOffers(props, store)
            await userEvent.click(
              await screen.findByLabelText('Date limite de réservation')
            )
            await userEvent.click(screen.getByText('17'))

            // When
            await userEvent.click(screen.getByText('Enregistrer'))

            // Then
            const savedStocks = pcapi.bulkCreateOrEditStock.mock.calls[0][1]
            expect(savedStocks[0].bookingLimitDatetime).toBe(
              '2020-12-17T22:59:59Z'
            )
          })

          it('should set booking limit datetime to null when not specified', async () => {
            // Given
            pcapi.bulkCreateOrEditStock.mockResolvedValue({})
            await renderOffers(props, store)

            fireEvent.change(
              await screen.findByLabelText('Date limite de réservation'),
              {
                target: { value: null },
              }
            )

            // When
            await userEvent.click(screen.getByText('Enregistrer'))

            // Then
            const savedStocks = pcapi.bulkCreateOrEditStock.mock.calls[0][1]
            expect(savedStocks[0].bookingLimitDatetime).toBeNull()
          })

          it('should set quantity to null when not specified', async () => {
            // Given
            pcapi.bulkCreateOrEditStock.mockResolvedValue({})
            await renderOffers(props, store)
            fireEvent.change(await screen.findByLabelText('Quantité'), {
              target: { value: null },
            })

            // When
            await userEvent.click(screen.getByText('Enregistrer'))
            // Then
            const savedStocks = pcapi.bulkCreateOrEditStock.mock.calls[0][1]
            expect(savedStocks[0].quantity).toBeNull()
          })

          it('should display price error when the price is above 300 euros and offer is not educational', async () => {
            // Given
            await renderOffers(props, store)
            fireEvent.change(await screen.findByLabelText('Prix'), {
              target: { value: '301' },
            })

            // When
            await userEvent.click(screen.getByText('Enregistrer'))

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
            pcapi.bulkCreateOrEditStock.mockRejectedValueOnce({
              errors: {
                price: 'Le prix est invalide.',
                quantity: 'La quantité est invalide.',
              },
            })
            await renderOffers(props, store)

            fireEvent.change(await screen.findByLabelText('Quantité'), {
              target: { value: '10' },
            })

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

            fireEvent.change(await screen.findByLabelText('Prix'), {
              target: { value: '-10' },
            })
            fireEvent.change(screen.getByLabelText('Quantité'), {
              target: { value: '-20' },
            })

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

            fireEvent.change(await screen.findByLabelText('Quantité'), {
              target: { value: '10' },
            })

            // When
            await userEvent.click(screen.getByText('Enregistrer'))

            // Then
            const errorMessage = await screen.findByText(
              'Vos stocks ont bien été sauvegardés.'
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
          jest
            .spyOn(apiV1, 'getOffersGetOffer')
            .mockResolvedValue(synchronisedThingOffer)
        })

        it('should not be able to edit a stock', async () => {
          // When
          await renderOffers(props, store)

          // Then
          expect(await screen.findByLabelText('Prix')).toBeDisabled()
          expect(
            screen.getByLabelText('Date limite de réservation')
          ).toBeDisabled()
          expect(screen.getByLabelText('Quantité')).toBeDisabled()
        })

        it('should not be able to delete a stock', async () => {
          // Given
          await renderOffers(props, store)
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
            .spyOn(apiV1, 'getOffersGetOffer')
            .mockResolvedValue({ ...thingOffer, isDigital: true })
          await renderOffers(props, store)

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
        await renderOffers(props, store)

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

  describe('create', () => {
    it('should not display offer status', async () => {
      // Given
      const draftOffer = {
        ...defaultOffer,
        status: 'DRAFT',
      }
      jest.spyOn(apiV1, 'getOffersGetOffer').mockResolvedValueOnce(draftOffer)

      // When
      await renderOffers(props, store)

      // Then
      expect(screen.queryByText('brouillon')).not.toBeInTheDocument()
    })

    it('should display a specific success notification when the user has finished the offer creation process', async () => {
      // Given
      const draftOffer = offerFactory({
        name: 'mon offre',
        id: 'AG3A',
        status: 'DRAFT',
      })

      jest.spyOn(apiV1, 'getOffersGetOffer').mockResolvedValue(draftOffer)
      pcapi.bulkCreateOrEditStock.mockResolvedValue({})

      await renderOffers(props, store)

      await userEvent.click(await screen.findByText('Ajouter un stock'))
      fireEvent.change(screen.getByLabelText('Prix'), {
        target: { value: '15' },
      })

      // When
      await userEvent.click(screen.getByText('Valider et créer l’offre'))

      // Then
      const successMessage = await screen.findByText(
        'Votre offre a bien été créée et vos stocks sauvegardés.'
      )
      expect(successMessage).toBeInTheDocument()
    })

    it('should redirect to confirmation page after stocks validation', async () => {
      // Given
      const offerDraftStatus = offerFactory({
        name: 'mon offre',
        id: 'AG3A',
        status: 'DRAFT',
      })
      const offerApprovedStatus = offerFactory({
        name: 'mon offre',
        id: 'AG3A',
        status: 'APPROVED',
      })
      jest
        .spyOn(apiV1, 'getOffersGetOffer')
        .mockResolvedValueOnce(offerDraftStatus)
        .mockResolvedValueOnce(offerApprovedStatus)
      loadFakeApiStocks([])
      bulkFakeApiCreateOrEditStock({ id: 'createdStock' })
      await renderOffers(props, store)
      await userEvent.click(
        await screen.findByText('Ajouter un stock', { selector: 'button' })
      )
      fireEvent.change(screen.getByLabelText('Prix'), { target: { value: 20 } })

      // When
      await userEvent.click(
        screen.getByText('Valider et créer l’offre', { selector: 'button' })
      )

      // Then
      await expect(
        screen.findByText('Offre créée !', { selectof: 'h2' })
      ).resolves.toBeInTheDocument()
    })

    it('should redirect to confirmation page with pending message when offer is pending validation', async () => {
      // Given
      const offerDraftStatus = offerFactory({
        name: 'mon offre',
        id: 'AG3A',
        status: 'DRAFT',
      })
      const offerPendingStatus = offerFactory({
        name: 'mon offre',
        id: 'AG3A',
        status: 'PENDING',
      })
      jest
        .spyOn(apiV1, 'getOffersGetOffer')
        .mockResolvedValueOnce(offerDraftStatus)
        .mockResolvedValueOnce(offerPendingStatus)
      loadFakeApiStocks([])
      bulkFakeApiCreateOrEditStock({ id: 'createdStock' })
      await renderOffers(props, store)
      await userEvent.click(
        await screen.findByText('Ajouter un stock', { selector: 'button' })
      )
      fireEvent.change(screen.getByLabelText('Prix'), { target: { value: 20 } })

      // When
      await userEvent.click(
        screen.getByText('Valider et créer l’offre', { selector: 'button' })
      )

      // Then
      await expect(
        screen.findByText('Offre en cours de validation', { selectof: 'h2' })
      ).resolves.toBeInTheDocument()
    })

    describe('event offer', () => {
      let noStockOffer
      beforeEach(() => {
        noStockOffer = {
          ...defaultOffer,
          isEvent: true,
          stocks: [],
        }

        jest.spyOn(apiV1, 'getOffersGetOffer').mockResolvedValue(noStockOffer)
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
        const eventsDates = screen.getAllByLabelText('Date de l’événement')
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
        expect(screen.getByLabelText('Date de l’événement').value).toBe('')
        expect(screen.getByLabelText('Heure de l’événement').value).toBe('')
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
          screen.getAllByLabelText('Date de l’événement')[0]
        )
        await userEvent.click(screen.getByText('24'))

        await userEvent.click(
          screen.getAllByLabelText('Heure de l’événement')[0]
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
          screen.getAllByLabelText('Date de l’événement')[0]
        )
        await userEvent.click(screen.getByText('25'))

        await userEvent.click(
          screen.getAllByLabelText('Heure de l’événement')[0]
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
        await userEvent.click(screen.getByText('Enregistrer'))

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

        await userEvent.click(screen.getByLabelText('Date de l’événement'))
        await userEvent.click(screen.getByText('24'))

        await userEvent.click(screen.getByLabelText('Heure de l’événement'))
        await userEvent.click(screen.getByText('20:00'))

        // When
        fireEvent.change(screen.getByLabelText('Prix'), {
          target: { value: '301' },
        })
        await userEvent.click(screen.getByText('Enregistrer'))

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

        await userEvent.click(screen.getByLabelText('Date de l’événement'))
        await userEvent.click(screen.getByText('26'))

        await userEvent.click(screen.getByLabelText('Heure de l’événement'))
        await userEvent.click(screen.getByText('20:00'))

        fireEvent.change(screen.getByLabelText('Prix'), {
          target: { value: '10' },
        })

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
        await userEvent.click(await screen.findByText('Ajouter une date'))

        await userEvent.click(screen.getByLabelText('Date de l’événement'))
        await userEvent.click(screen.getByText('26'))

        await userEvent.click(screen.getByLabelText('Heure de l’événement'))
        await userEvent.click(screen.getByText('20:00'))

        fireEvent.change(screen.getByLabelText('Prix'), {
          target: { value: '-10' },
        })
        fireEvent.change(screen.getByLabelText('Quantité'), {
          target: { value: '-20' },
        })

        // When
        await userEvent.click(screen.getByText('Enregistrer'))

        // Then
        const errorMessage = await screen.findByText(
          'Une ou plusieurs erreurs sont présentes dans le formulaire.'
        )
        expect(errorMessage).toBeInTheDocument()
        expect(screen.getByLabelText('Prix')).toHaveClass('error')
        expect(screen.getByLabelText('Quantité')).toHaveClass('error')
        expect(pcapi.bulkCreateOrEditStock).toHaveBeenCalledTimes(0)
      })

      it('should display success message on success', async () => {
        // Given
        pcapi.bulkCreateOrEditStock.mockResolvedValueOnce({})
        await renderOffers(props, store)
        await userEvent.click(await screen.findByText('Ajouter une date'))

        await userEvent.click(screen.getByLabelText('Date de l’événement'))
        await userEvent.click(screen.getByText('26'))

        await userEvent.click(screen.getByLabelText('Heure de l’événement'))
        await userEvent.click(screen.getByText('20:00'))

        fireEvent.change(screen.getByLabelText('Prix'), {
          target: { value: '10' },
        })

        // When
        await userEvent.click(screen.getByText('Enregistrer'))

        // Then
        const errorMessage = await screen.findByText(
          'Vos stocks ont bien été sauvegardés.'
        )
        expect(errorMessage).toBeInTheDocument()
      })

      it('should redirect offer with stock to confirmation page after offer creation', async () => {
        // Given
        const offerDraftStatus = offerFactory({
          name: 'mon offre',
          id: 'AG3A',
          isEvent: true,
          status: 'DRAFT',
        })
        const offerApprovedStatus = offerFactory({
          name: 'mon offre',
          id: 'AG3A',
          status: 'APPROVED',
        })
        jest
          .spyOn(apiV1, 'getOffersGetOffer')
          .mockResolvedValueOnce(offerDraftStatus)
          .mockResolvedValueOnce(offerApprovedStatus)
        loadFakeApiStocks([])
        bulkFakeApiCreateOrEditStock({ id: 'createdStock' })
        await renderOffers(
          props,
          store,
          '/offre/AG3A/individuel/creation/stocks'
        )
        await userEvent.click(await screen.findByText('Ajouter une date'))

        await userEvent.click(screen.getByLabelText('Date de l’événement'))
        await userEvent.click(screen.getByText('26'))

        await userEvent.click(screen.getByLabelText('Heure de l’événement'))
        await userEvent.click(screen.getByText('20:00'))

        fireEvent.change(screen.getByLabelText('Prix'), {
          target: { value: '10' },
        })

        // When
        await userEvent.click(
          screen.getByText('Valider et créer l’offre', { selector: 'button' })
        )

        // Then
        const successMessage = screen.queryByText(
          'Votre offre a bien été créée et vos stocks sauvegardés.'
        )
        expect(successMessage).toBeInTheDocument()

        await expect(
          screen.findByText('Offre créée !', { selectof: 'h2' })
        ).resolves.toBeInTheDocument()
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

        jest.spyOn(apiV1, 'getOffersGetOffer').mockResolvedValue(noStockOffer)
      })

      it('should not display add activation codes option when not digital', async () => {
        // given
        const digitalOffer = {
          ...noStockOffer,
          isDigital: false,
        }
        jest.spyOn(apiV1, 'getOffersGetOffer').mockResolvedValue(digitalOffer)
        await renderOffers(props, store)

        // when
        await userEvent.click(await screen.findByText('Ajouter un stock'))

        // then
        expect(
          screen.queryByText('Ajouter des codes d’activation')
        ).not.toBeInTheDocument()
      })

      it('should not display remaining stocks and bookings columns when no stocks yet', async () => {
        // given
        const thingOffer = {
          ...defaultOffer,
          isEvent: false,
          stocks: [],
        }
        jest.spyOn(apiV1, 'getOffersGetOffer').mockResolvedValue(thingOffer)
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
        jest.spyOn(apiV1, 'getOffersGetOffer').mockResolvedValue(thingOffer)
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
        const createdStock = {
          activationCodes: [],
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
        await userEvent.click(screen.getByText('Enregistrer'))

        // then
        expect(pcapi.bulkCreateOrEditStock).toHaveBeenCalledWith('AG3A', [
          {
            bookingLimitDatetime: '2020-12-23T02:59:59Z',
            price: '15',
            quantity: '15',
          },
        ])
      })

      it('should display price error when the price is above 300 euros and offer is not educational', async () => {
        // Given
        await renderOffers(props, store)

        await userEvent.click(await screen.findByText('Ajouter un stock'))
        fireEvent.change(screen.getByLabelText('Prix'), {
          target: { value: '301' },
        })

        // When
        await userEvent.click(screen.getByText('Enregistrer'))

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
        await userEvent.click(await screen.findByText('Ajouter un stock'))

        fireEvent.change(screen.getByLabelText('Prix'), {
          target: { value: '-10' },
        })
        fireEvent.change(screen.getByLabelText('Quantité'), {
          target: { value: '-20' },
        })

        // When
        await userEvent.click(screen.getByText('Enregistrer'))

        // Then
        const errorMessage = await screen.findByText(
          'Une ou plusieurs erreurs sont présentes dans le formulaire.'
        )
        expect(errorMessage).toBeInTheDocument()
        expect(screen.getByLabelText('Prix')).toHaveClass('error')
        expect(screen.getByLabelText('Quantité')).toHaveClass('error')
        expect(pcapi.bulkCreateOrEditStock).toHaveBeenCalledTimes(0)
      })

      it('should display success message on success', async () => {
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
        await userEvent.click(screen.getByText('Enregistrer'))

        // Then
        const errorMessage = await screen.findByText(
          'Vos stocks ont bien été sauvegardés.'
        )
        expect(errorMessage).toBeInTheDocument()
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

      describe('digital offer', () => {
        let digitalOffer
        beforeEach(() => {
          digitalOffer = {
            ...defaultOffer,
            isDigital: true,
            isEvent: false,
            stocks: [],
          }

          jest.spyOn(apiV1, 'getOffersGetOffer').mockResolvedValue(digitalOffer)
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
          jest.spyOn(apiV1, 'getOffersGetOffer').mockResolvedValue(eventOffer)
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

          await userEvent.click(screen.getByText('Enregistrer'))

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

          await userEvent.click(screen.getByText('Enregistrer'))

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

          jest.spyOn(apiV1, 'getOffersGetOffer').mockResolvedValue(offer)
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
            screen.findByText('Enregistrer')
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
