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
import { offerFactory, stockFactory } from 'utils/apiFactories'
import { loadFakeApiStocks } from 'utils/fakeApi'

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
    jest.spyOn(api, 'getOffer').mockResolvedValue(defaultOffer)
    pcapi.loadStocks.mockResolvedValue({ stocks: [] })
    pcapi.loadCategories.mockResolvedValue({
      categories: [],
      subcategories: [],
    })
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
        expect(
          screen.queryByText('Enregistrer les modifacations')
        ).not.toBeInTheDocument()
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
      jest.spyOn(api, 'getOffer').mockResolvedValue(offerWithMultipleStocks)
      pcapi.loadStocks.mockResolvedValue({ stocks })

      // when
      await renderOffers(props, store)

      // then
      const beginningDatetimeFields = await screen.findAllByLabelText(
        'Date de l’évènement'
      )
      const hourFields = await screen.findAllByLabelText('Heure de l’évènement')
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

    it('should have cancel link to go back to offers list', async () => {
      // given
      const offer = {
        ...defaultOffer,
        stocks: [],
      }

      jest.spyOn(api, 'getOffer').mockResolvedValue(offer)
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
      expect(cancelLink).toHaveAttribute('href', '/offres')
    })

    describe('when offer is being created (DRAFT status)', () => {
      beforeEach(() => {
        const draftOffer = {
          ...defaultOffer,
          status: 'DRAFT',
        }

        jest.spyOn(api, 'getOffer').mockResolvedValue(draftOffer)
      })

      describe('when no stock yet', () => {
        it('should display a disabled "Valider et créer l’offre" button', async () => {
          // Given
          pcapi.loadStocks.mockResolvedValue({ stocks: [] })

          // When
          await renderOffers(props, store)

          // Then
          expect(
            await screen.findByText('Étape suivante', {
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
            await screen.findByText('Étape suivante', {
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
        jest.spyOn(api, 'getOffer').mockResolvedValue(offer)
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
        expect(screen.getByLabelText('Date de l’évènement')).toBeDisabled()
        expect(screen.getByLabelText('Heure de l’évènement')).toBeDisabled()
        expect(screen.getByLabelText('Prix')).toBeDisabled()
        expect(
          screen.getByLabelText('Date limite de réservation')
        ).toBeDisabled()
        expect(screen.getByLabelText('Quantité')).toBeDisabled()
        expect(screen.getByTitle('Supprimer le stock')).toHaveAttribute(
          'aria-disabled',
          'true'
        )
        expect(screen.getByText('Enregistrer les modifications')).toBeDisabled()
      })

      it('should display status informative message and disable all fields when offer is pending for validation', async () => {
        // given
        offer.status = 'PENDING'
        offer.isActive = true
        jest.spyOn(api, 'getOffer').mockResolvedValue(offer)
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
        expect(screen.getByLabelText('Date de l’évènement')).toBeDisabled()
        expect(screen.getByLabelText('Heure de l’évènement')).toBeDisabled()
        expect(screen.getByLabelText('Prix')).toBeDisabled()
        expect(
          screen.getByLabelText('Date limite de réservation')
        ).toBeDisabled()
        expect(screen.getByLabelText('Quantité')).toBeDisabled()
        expect(screen.getByTitle('Supprimer le stock')).toHaveAttribute(
          'aria-disabled',
          'true'
        )
        expect(screen.getByText('Enregistrer les modifications')).toBeDisabled()
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

        jest.spyOn(api, 'getOffer').mockResolvedValue(eventOffer)
        pcapi.loadStocks.mockResolvedValue({ stocks: [eventStock] })
      })

      it('should display an information message regarding booking cancellation', async () => {
        // when
        await renderOffers(props, store)

        // then
        const informationMessage = await screen.findByText(
          'Les utilisateurs ont un délai de 48h pour annuler leur réservation mais ne peuvent pas le faire moins de 48h avant le début de l’évènement. Si la date limite de réservation n’est pas encore passée, la place est alors automatiquement remise en vente.'
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
        expect(api.getOffer).toHaveBeenCalledWith('AG3A')

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
        jest.spyOn(api, 'getOffer').mockResolvedValue(thingOffer)
        pcapi.loadStocks.mockResolvedValue({ stocks: [{ ...defaultStock }] })
      })

      it('should display an information message regarding booking cancellation with 10 days auto expiry when subcategory is LIVRE_PAPIER', async () => {
        // given
        thingOffer.subcategoryId = 'LIVRE_PAPIER'
        jest.spyOn(api, 'getOffer').mockResolvedValue(thingOffer)

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
        expect(api.getOffer).toHaveBeenCalledWith('AG3A')

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
          jest.spyOn(api, 'getOffer').mockResolvedValue(synchronisedThingOffer)
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
        jest.spyOn(api, 'getOffer').mockResolvedValue(digitalOffer)
        pcapi.loadStocks.mockResolvedValue({ stocks: [{ ...defaultStock }] })
      })

      it('should display an information message regarding booking cancellation', async () => {
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
        jest.spyOn(api, 'getOffer').mockResolvedValue(offer)
        loadFakeApiStocks([stock])
        // do not resolve promise so that button remains in disabled state
        jest
          .spyOn(pcapi, 'bulkCreateOrEditStock')
          .mockImplementation(() => new Promise(() => {}))
        await renderOffers(props, store)
        const submitButton = await screen.findByRole('button', {
          type: 'submit',
          name: 'Enregistrer les modifications',
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

        jest.spyOn(api, 'getOffer').mockResolvedValue(eventOffer)
        pcapi.loadStocks.mockResolvedValue({ stocks: [] })
        pcapi.bulkCreateOrEditStock.mockResolvedValue({})

        await renderOffers(props, store)

        await userEvent.click(await screen.findByText('Ajouter une date'))
        await userEvent.click(screen.getByLabelText('Date de l’évènement'))
        await userEvent.click(screen.getByText('26'))
        await userEvent.click(screen.getByLabelText('Heure de l’évènement'))
        await userEvent.click(screen.getByText('20:00'))
        const submitButton = screen.getByText('Enregistrer les modifications', {
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

      jest.spyOn(api, 'getOffer').mockResolvedValue(eventOffer)
      pcapi.loadStocks.mockResolvedValue({ stocks: [] })
      pcapi.bulkCreateOrEditStock.mockResolvedValue({})
    })

    it('should have mandatory beginning date field for event offer', async () => {
      // Given
      await renderOffers(props, store)

      await userEvent.click(await screen.findByText('Ajouter une date'))

      await userEvent.click(screen.getByLabelText('Heure de l’évènement'))
      await userEvent.click(screen.getByText('20:00'))

      fireEvent.change(screen.getByLabelText('Prix'), {
        target: { value: '10' },
      })

      // When
      await userEvent.click(screen.getByText('Enregistrer les modifications'))

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

      await userEvent.click(screen.getByLabelText('Date de l’évènement'))
      await userEvent.click(screen.getByText('26'))

      fireEvent.change(screen.getByLabelText('Prix'), {
        target: { value: '10' },
      })

      // When
      await userEvent.click(screen.getByText('Enregistrer les modifications'))

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

      await userEvent.click(screen.getByLabelText('Date de l’évènement'))
      await userEvent.click(screen.getByText('26'))

      await userEvent.click(screen.getByLabelText('Heure de l’évènement'))
      await userEvent.click(screen.getByText('20:00'))

      // When
      await userEvent.click(screen.getByText('Enregistrer les modifications'))

      // Then
      const errorMessage = await screen.findByText(
        'Une ou plusieurs erreurs sont présentes dans le formulaire.'
      )
      expect(errorMessage).toBeInTheDocument()
    })
  })
})
