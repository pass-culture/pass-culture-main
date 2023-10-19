import { screen, waitFor } from '@testing-library/react'
import { userEvent } from '@testing-library/user-event'
import format from 'date-fns/format'
import React from 'react'
import { Route, Routes } from 'react-router-dom'

import { api } from 'apiClient/api'
import { ApiError, GetIndividualOfferResponseModel } from 'apiClient/v1'
import { ApiRequestOptions } from 'apiClient/v1/core/ApiRequestOptions'
import { ApiResult } from 'apiClient/v1/core/ApiResult'
import { OFFER_WIZARD_STEP_IDS } from 'components/IndividualOfferBreadcrumb/constants'
import Notification from 'components/Notification/Notification'
import {
  IndividualOfferContextValues,
  IndividualOfferContext,
} from 'context/IndividualOfferContext'
import {
  LIVRE_PAPIER_SUBCATEGORY_ID,
  OFFER_WIZARD_MODE,
} from 'core/Offers/constants'
import { IndividualOffer } from 'core/Offers/types'
import {
  getIndividualOfferPath,
  getIndividualOfferUrl,
} from 'core/Offers/utils/getIndividualOfferUrl'
import { offerVenueFactory } from 'utils/apiFactories'
import { FORMAT_ISO_DATE_ONLY } from 'utils/date'
import {
  individualOfferContextFactory,
  individualOfferFactory,
  individualOfferSubCategoryFactory,
  individualStockFactory,
} from 'utils/individualApiFactories'
import { renderWithProviders } from 'utils/renderWithProviders'

import { serializeThingBookingLimitDatetime } from '../adapters/serializers'
import StocksThing, { StocksThingProps } from '../StocksThing'

vi.mock('utils/date', async () => {
  return {
    ...((await vi.importActual('utils/date')) ?? {}),
    getToday: vi
      .fn()
      .mockImplementation(() => new Date('2020-12-15T12:00:00Z')),
  }
})

const renderStockThingScreen = (
  props: StocksThingProps,
  contextValue: IndividualOfferContextValues
) =>
  renderWithProviders(
    <>
      <Routes>
        <Route
          path={getIndividualOfferPath({
            step: OFFER_WIZARD_STEP_IDS.STOCKS,
            mode: OFFER_WIZARD_MODE.CREATION,
          })}
          element={
            <IndividualOfferContext.Provider value={contextValue}>
              <StocksThing {...props} />
            </IndividualOfferContext.Provider>
          }
        />
        <Route
          path={getIndividualOfferPath({
            step: OFFER_WIZARD_STEP_IDS.SUMMARY,
            mode: OFFER_WIZARD_MODE.CREATION,
          })}
          element={<div>Next page</div>}
        />
      </Routes>
      <Notification />
    </>,
    {
      initialRouterEntries: [
        getIndividualOfferUrl({
          step: OFFER_WIZARD_STEP_IDS.STOCKS,
          mode: OFFER_WIZARD_MODE.CREATION,
          offerId: contextValue.offer?.id || undefined,
        }),
      ],
    }
  )

describe('screens:StocksThing', () => {
  let props: StocksThingProps
  let contextValue: IndividualOfferContextValues
  let offer: IndividualOffer
  const offerId = 1

  beforeEach(() => {
    offer = individualOfferFactory({
      id: offerId,
      venue: offerVenueFactory({
        departementCode: '75',
      }),
      stocks: [],
      lastProviderName: 'Ciné Office',
      subcategoryId: 'CANBEDUO',
    })
    props = {
      offer,
    }
    contextValue = individualOfferContextFactory({
      offerId: offerId,
      offer,
      subCategories: [
        individualOfferSubCategoryFactory({ id: 'CANBEDUO', canBeDuo: true }),
      ],
    })
    vi.spyOn(api, 'getOffer').mockResolvedValue(
      {} as GetIndividualOfferResponseModel
    )
    vi.spyOn(api, 'patchOffer').mockResolvedValue(
      {} as GetIndividualOfferResponseModel
    )
  })

  it('should render physical stock thing', () => {
    props.offer = {
      ...offer,
      isDigital: false,
    }

    renderStockThingScreen(props, contextValue)
    expect(screen.getByTestId('stock-thing-form')).toBeInTheDocument()
    expect(
      screen.getByText(
        'Les bénéficiaires ont 30 jours pour faire valider leur contremarque. Passé ce délai, la réservation est automatiquement annulée et l’offre remise en vente.'
      )
    ).toBeInTheDocument()

    expect(screen.getByLabelText('Prix')).toBeInTheDocument()
    expect(
      screen.getByLabelText('Date limite de réservation')
    ).toBeInTheDocument()
    expect(screen.getByLabelText('Quantité')).toBeInTheDocument()
  })

  it('should render digital stock thing', () => {
    props.offer = {
      ...offer,
      subcategoryId: 'TESTID',
      isDigital: true,
    }
    renderStockThingScreen(props, contextValue)
    expect(
      screen.getByText(
        /Les bénéficiaires ont 30 jours pour annuler leurs réservations d’offres numériques. Dans le cas d’offres avec codes d’activation, les bénéficiaires ne peuvent pas annuler leurs réservations. Toute réservation est définitive et sera immédiatement validée. Pour ajouter des codes d’activation, veuillez passer par le menu ··· et choisir l’option correspondante./
      )
    ).toBeInTheDocument()
    expect(
      screen.queryByText('Comment gérer les codes d’activation')
    ).not.toBeInTheDocument()
  })

  it('should render digital book', () => {
    props.offer = {
      ...offer,
      subcategoryId: LIVRE_PAPIER_SUBCATEGORY_ID,
      isDigital: false,
    }
    renderStockThingScreen(props, contextValue)
    expect(
      screen.getByText(
        'Les bénéficiaires ont 10 jours pour faire valider leur contremarque. Passé ce délai, la réservation est automatiquement annulée et l’offre remise en vente.'
      )
    ).toBeInTheDocument()
    expect(
      screen.queryByText('Comment gérer les codes d’activation')
    ).not.toBeInTheDocument()
  })

  it('should submit stock form when click on "Enregistrer et continuer"', async () => {
    vi.spyOn(api, 'upsertStocks').mockResolvedValue({
      stocks: [],
    })
    renderStockThingScreen(props, contextValue)
    const nextButton = screen.getByRole('button', {
      name: 'Enregistrer et continuer',
    })
    await userEvent.type(screen.getByLabelText('Prix'), '20')
    await userEvent.click(nextButton)

    await waitFor(() => {
      expect(api.upsertStocks).toHaveBeenCalledWith({
        offerId: offer.id,
        stocks: [
          {
            bookingLimitDatetime: null,
            price: 20,
            quantity: null,
          },
        ],
      })
    })
    expect(screen.getByText('Next page')).toBeInTheDocument()
    expect(api.getOffer).toHaveBeenCalledWith(offer.id)
  })

  it('should submit stock form with duo informations when clicking on on "Enregistrer et continuer"', async () => {
    vi.spyOn(api, 'upsertStocks').mockResolvedValue({
      stocks: [],
    })
    renderStockThingScreen(props, contextValue)
    const nextButton = screen.getByRole('button', {
      name: 'Enregistrer et continuer',
    })
    await userEvent.type(screen.getByLabelText('Prix'), '20')
    await userEvent.click(
      screen.getByLabelText('Accepter les réservations “Duo“')
    )
    await userEvent.click(nextButton)

    await waitFor(() => {
      expect(api.patchOffer).toHaveBeenCalledWith(
        offer.id,
        expect.objectContaining({ isDuo: true })
      )
    })
    expect(screen.getByText('Next page')).toBeInTheDocument()
    expect(api.getOffer).toHaveBeenCalledWith(offer.id)
  })

  it('should not submit stock form when click on "Retour"', async () => {
    vi.spyOn(api, 'upsertStocks').mockResolvedValue({
      stocks: [],
    })

    renderStockThingScreen(props, contextValue)

    await userEvent.click(screen.getByRole('button', { name: 'Retour' }))
    expect(api.upsertStocks).not.toHaveBeenCalled()
    expect(
      screen.queryByText('Brouillon sauvegardé dans la liste des offres')
    ).not.toBeInTheDocument()
    expect(api.getOffer).not.toHaveBeenCalledWith('OFFER_ID')
  })

  it('should display api errors', async () => {
    vi.spyOn(api, 'upsertStocks').mockRejectedValue(
      new ApiError(
        {} as ApiRequestOptions,
        {
          status: 400,
          body: {
            price: 'API price ERROR',
            quantity: 'API quantity ERROR',
            bookingLimitDatetime: 'API bookingLimitDatetime ERROR',
          },
        } as ApiResult,
        ''
      )
    )

    renderStockThingScreen(props, contextValue)

    await userEvent.type(screen.getByLabelText('Prix'), '20')
    await userEvent.click(
      screen.getByRole('button', { name: 'Enregistrer et continuer' })
    )

    await waitFor(() => {
      expect(screen.getByText('API price ERROR')).toBeInTheDocument()
    })
    expect(screen.getByText('API quantity ERROR')).toBeInTheDocument()
    expect(
      screen.getByText('API bookingLimitDatetime ERROR')
    ).toBeInTheDocument()
  })

  describe('activation codes', () => {
    it('should submit activation codes and freeze quantity when a csv is provided', async () => {
      vi.spyOn(api, 'upsertStocks').mockResolvedValue({
        stocks: [],
      })
      props.offer = {
        ...offer,
        isDigital: true,
      }
      renderStockThingScreen(props, contextValue)

      await userEvent.type(screen.getByLabelText('Prix'), '20')

      await userEvent.click(
        screen.getByTestId('stock-form-actions-button-open')
      )

      // userEvent.dblClick to fix @reach/menu-button update, to delete after refactor
      await userEvent.dblClick(
        screen.getByText("Ajouter des codes d'activation")
      )
      const uploadButton = screen.getByText(
        "Importer un fichier .csv depuis l'ordinateur"
      )

      const file = new File(
        ['ABH\nJHB\nIOP\nKLM\nMLK'],
        'activation_codes.csv',
        {
          type: 'text/csv',
        }
      )
      await userEvent.upload(uploadButton, file)

      await expect(
        screen.findByText(
          'Vous êtes sur le point d’ajouter 5 codes d’activation.'
        )
      ).resolves.toBeInTheDocument()

      const today = format(new Date(), FORMAT_ISO_DATE_ONLY)
      await userEvent.type(
        await screen.findByText('Date limite de validité'),
        today
      )

      await userEvent.click(screen.getByText('Valider'))
      expect(screen.getByLabelText('Quantité')).toBeDisabled()

      const priceInput = screen.getByLabelText('Prix')
      await userEvent.clear(priceInput)
      await userEvent.type(priceInput, '14.01')
      const expirationInput = screen.getByLabelText("Date d'expiration")
      expect(expirationInput).toBeDisabled()
      const date = new Date()
      date.setUTCHours(22, 59, 59, 999)
      expect(expirationInput).toHaveValue(today)
      await userEvent.click(screen.getByText('Enregistrer et continuer'))
      expect(api.upsertStocks).toHaveBeenCalledWith({
        offerId: offer.id,
        stocks: [
          {
            bookingLimitDatetime: null,
            price: 14.01,
            quantity: 5,
            activationCodes: ['ABH', 'JHB', 'IOP', 'KLM', 'MLK'],
            activationCodesExpirationDatetime:
              serializeThingBookingLimitDatetime(date, '75'),
          },
        ],
      })
    })

    it('should display an error when activation code file is incorrect', async () => {
      vi.spyOn(api, 'upsertStocks').mockResolvedValue({
        stocks: [],
      })
      props.offer = {
        ...offer,
        isDigital: true,
      }
      renderStockThingScreen(props, contextValue)

      await userEvent.click(
        screen.getByTestId('stock-form-actions-button-open')
      )
      await userEvent.dblClick(
        screen.getByText("Ajouter des codes d'activation")
      )
      const uploadButton = screen.getByText(
        "Importer un fichier .csv depuis l'ordinateur"
      )
      const title = screen.getByText(/Ajouter des codes d’activation/)

      const file = new File(
        ['ABH\nJHB\nIOP\nKLM\nABH'],
        'activation_codes.csv',
        {
          type: 'text/csv',
        }
      )
      await userEvent.upload(uploadButton, file)

      await expect(
        screen.findByText(
          "Une erreur s'est produite lors de l’import de votre fichier."
        )
      ).resolves.toBeInTheDocument()

      await userEvent.click(screen.getByTitle('Fermer la modale'))
      expect(title).not.toBeInTheDocument()
    })

    it('should display an expiration field disabled when activationCodesExpirationDatetime is provided', () => {
      props.offer = {
        ...offer,
        isDigital: true,
        stocks: [
          individualStockFactory({
            bookingsQuantity: 1,
            price: 12,
            hasActivationCode: true,
            activationCodesExpirationDatetime: new Date('2020-12-15T12:00:00Z'),
          }),
        ],
      }
      renderStockThingScreen(props, contextValue)

      expect(screen.getByLabelText('Quantité')).toBeDisabled()
      const expirationInput = screen.getByLabelText("Date d'expiration")
      expect(expirationInput).toBeDisabled()
      expect(expirationInput).toHaveValue('2020-12-15')
    })
  })

  const setNumberPriceValue = [
    { value: '20', expectedNumber: 20 },
    { value: 'azer', expectedNumber: null },
    { value: 'AZER', expectedNumber: null },
    { value: '2fsqjk', expectedNumber: 2 },
    { value: '2fsqm0', expectedNumber: 20 },
  ]
  it.each(setNumberPriceValue)(
    'should only type numbers for price input',
    async ({ value, expectedNumber }) => {
      renderStockThingScreen(props, contextValue)

      const priceInput = screen.getByLabelText('Prix', {
        exact: false,
      })
      await userEvent.type(priceInput, value)
      expect(priceInput).toHaveValue(expectedNumber)
    }
  )

  const setNumberQuantityValue = [
    { value: '20', expectedNumber: 20 },
    { value: '20.37', expectedNumber: 2037 },
    { value: 'AZER', expectedNumber: null },
    { value: '2fsqjk', expectedNumber: 2 },
    { value: '2fsqm0', expectedNumber: 20 },
  ]
  it.each(setNumberQuantityValue)(
    'should only type numbers for quantity input',
    async ({ value, expectedNumber }) => {
      renderStockThingScreen(props, contextValue)

      const quantityInput = screen.getByLabelText('Quantité', {
        exact: false,
      })
      await userEvent.type(quantityInput, value)
      expect(quantityInput).toHaveValue(expectedNumber)
    }
  )
})
