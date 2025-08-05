import { api } from 'apiClient/api'
import {
  ApiError,
  GetIndividualOfferResponseModel,
  GetIndividualOfferWithAddressResponseModel,
  GetOfferStockResponseModel,
  SubcategoryIdEnum,
} from 'apiClient/v1'
import { ApiRequestOptions } from 'apiClient/v1/core/ApiRequestOptions'
import { ApiResult } from 'apiClient/v1/core/ApiResult'
import { screen, waitFor } from '@testing-library/react'
import { userEvent } from '@testing-library/user-event'
import * as useAnalytics from 'app/App/analytics/firebase'
import {
  IndividualOfferContext,
  IndividualOfferContextValues,
} from 'commons/context/IndividualOfferContext/IndividualOfferContext'
import { Events } from 'commons/core/FirebaseEvents/constants'
import {
  INDIVIDUAL_OFFER_WIZARD_STEP_IDS,
  OFFER_WIZARD_MODE,
} from 'commons/core/Offers/constants'
import {
  getIndividualOfferPath,
  getIndividualOfferUrl,
} from 'commons/core/Offers/utils/getIndividualOfferUrl'
import { FORMAT_ISO_DATE_ONLY } from 'commons/utils/date'
import {
  getIndividualOfferFactory,
  getOfferStockFactory,
  getOfferVenueFactory,
  individualOfferContextValuesFactory,
  subcategoryFactory,
} from 'commons/utils/factories/individualApiFactories'
import { renderWithProviders } from 'commons/utils/renderWithProviders'
import { Notification } from 'components/Notification/Notification'
import { format } from 'date-fns'
import { Route, Routes } from 'react-router'
import { ButtonLink } from 'ui-kit/Button/ButtonLink'
import { expect } from 'vitest'

import { serializeThingBookingLimitDatetime } from '../adapters/serializers'
import { StocksThing, StocksThingProps } from '../StocksThing'

vi.mock('commons/utils/date', async () => {
  return {
    ...(await vi.importActual('commons/utils/date')),
    getToday: vi
      .fn()
      .mockImplementation(() => new Date('2020-12-15T12:00:00Z')),
  }
})

const renderStockThingScreen = async (
  stocks: GetOfferStockResponseModel[],
  props: StocksThingProps,
  contextValue: IndividualOfferContextValues
) => {
  vi.spyOn(api, 'getStocks').mockResolvedValue({
    stocks,
    stockCount: stocks.length,
    hasStocks: true,
  })
  renderWithProviders(
    <>
      <Routes>
        <Route
          path={getIndividualOfferPath({
            step: INDIVIDUAL_OFFER_WIZARD_STEP_IDS.STOCKS,
            mode: OFFER_WIZARD_MODE.CREATION,
          })}
          element={
            <IndividualOfferContext.Provider value={contextValue}>
              <StocksThing {...props} />
              <ButtonLink to="/outside">Go outside !</ButtonLink>
            </IndividualOfferContext.Provider>
          }
        />
        <Route
          path={getIndividualOfferPath({
            step: INDIVIDUAL_OFFER_WIZARD_STEP_IDS.SUMMARY,
            mode: OFFER_WIZARD_MODE.CREATION,
          })}
          element={<div>Next page</div>}
        />
        <Route
          path="/outside"
          element={<div>This is outside stock form</div>}
        />
      </Routes>
      <Notification />
    </>,
    {
      initialRouterEntries: [
        getIndividualOfferUrl({
          step: INDIVIDUAL_OFFER_WIZARD_STEP_IDS.STOCKS,
          mode: OFFER_WIZARD_MODE.CREATION,
          offerId: contextValue.offer?.id || undefined,
        }),
      ],
    }
  )
  await waitFor(() => {
    expect(api.getStocks).toHaveBeenCalledTimes(1)
  })
}

describe('screens:StocksThing', () => {
  let props: StocksThingProps
  let contextValue: IndividualOfferContextValues
  let offer: GetIndividualOfferWithAddressResponseModel
  let mockLogEvent = vi.fn()
  const offerId = 1

  beforeEach(() => {
    offer = getIndividualOfferFactory({
      id: offerId,
      venue: getOfferVenueFactory({
        departementCode: '75',
      }),
      subcategoryId: SubcategoryIdEnum.CINE_PLEIN_AIR,
    })
    props = {
      offer,
    }
    contextValue = individualOfferContextValuesFactory({
      offer,
      subCategories: [
        subcategoryFactory({
          id: SubcategoryIdEnum.CINE_PLEIN_AIR,
          canBeDuo: true,
        }),
      ],
    })
    vi.spyOn(api, 'getOffer').mockResolvedValue(
      {} as GetIndividualOfferWithAddressResponseModel
    )
    vi.spyOn(api, 'patchOffer').mockResolvedValue(
      {} as GetIndividualOfferResponseModel
    )

    vi.spyOn(useAnalytics, 'useAnalytics').mockImplementation(() => ({
      logEvent: mockLogEvent,
    }))
  })

  it('should render physical stock thing', async () => {
    props.offer = {
      ...offer,
      isDigital: false,
    }

    await renderStockThingScreen([], props, contextValue)
    expect(screen.getByTestId('stock-thing-form')).toBeInTheDocument()
    expect(
      screen.getByText(
        'Les bénéficiaires ont 30 jours pour faire valider leur contremarque. Passé ce délai, la réservation est automatiquement annulée et l’offre remise en vente.'
      )
    ).toBeInTheDocument()

    expect(screen.getByLabelText('Prix *')).toBeInTheDocument()
    expect(
      screen.getByLabelText('Date limite de réservation')
    ).toBeInTheDocument()
    expect(
      screen.getByLabelText('Quantité', {
        exact: false,
      })
    ).toBeInTheDocument()
  })

  it('should render digital stock thing', async () => {
    props.offer = {
      ...offer,
      isDigital: true,
    }
    await renderStockThingScreen([], props, contextValue)
    expect(
      screen.getByText(
        /Les bénéficiaires ont 30 jours pour annuler leurs réservations d’offres numériques./
      )
    ).toBeInTheDocument()
    expect(
      screen.queryByText('Comment gérer les codes d’activation')
    ).not.toBeInTheDocument()
  })

  it('should render digital book', async () => {
    props.offer = {
      ...offer,
      subcategoryId: SubcategoryIdEnum.LIVRE_PAPIER,
      isDigital: false,
    }
    await renderStockThingScreen([], props, contextValue)
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
    vi.spyOn(api, 'createThingStock').mockResolvedValue({
      id: 12,
    })
    await renderStockThingScreen([], props, contextValue)
    const nextButton = screen.getByRole('button', {
      name: 'Enregistrer et continuer',
    })
    await userEvent.type(screen.getByLabelText('Prix *'), '20')
    await userEvent.click(nextButton)

    await waitFor(() => {
      expect(api.createThingStock).toHaveBeenCalledWith({
        offerId: offer.id,
        bookingLimitDatetime: null,
        price: 20,
        quantity: null,
      })
    })
    expect(screen.getByText('Next page')).toBeInTheDocument()
    expect(api.getOffer).toHaveBeenCalledWith(offer.id)
  })

  it('should submit stock form with duo informations when clicking on on "Enregistrer et continuer"', async () => {
    vi.spyOn(api, 'createThingStock').mockResolvedValue({
      id: 12,
    })
    await renderStockThingScreen([], props, contextValue)
    const nextButton = screen.getByRole('button', {
      name: 'Enregistrer et continuer',
    })
    await userEvent.type(screen.getByLabelText('Prix *'), '20')
    await userEvent.click(
      screen.getByLabelText(/Accepter les réservations “Duo“/)
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

  it('should submit stock form when clicking on unlimited button "', async () => {
    vi.spyOn(api, 'createThingStock').mockResolvedValue({
      id: 12,
    })
    await renderStockThingScreen([], props, contextValue)
    const nextButton = screen.getByRole('button', {
      name: 'Enregistrer et continuer',
    })
    await userEvent.type(screen.getByLabelText('Prix *'), '20')
    await userEvent.type(screen.getByLabelText('Quantité'), '20')

    await userEvent.click(screen.getByLabelText(/Illimité/))
    await userEvent.click(nextButton)

    await waitFor(() => {
      expect(api.createThingStock).toHaveBeenCalledWith(
        expect.objectContaining({ quantity: null })
      )
    })
  })

  it('should not submit stock form when click on "Retour"', async () => {
    vi.spyOn(api, 'createThingStock').mockResolvedValue({
      id: 12,
    })
    vi.spyOn(api, 'updateThingStock').mockResolvedValue({
      id: 12,
    })

    await renderStockThingScreen([], props, contextValue)

    await userEvent.click(screen.getByRole('button', { name: 'Retour' }))
    expect(api.createThingStock).not.toHaveBeenCalled()
    expect(api.updateThingStock).not.toHaveBeenCalled()
    expect(
      screen.queryByText('Brouillon sauvegardé dans la liste des offres')
    ).not.toBeInTheDocument()
    expect(api.getOffer).not.toHaveBeenCalledWith('OFFER_ID')
  })

  it('should display api errors', async () => {
    vi.spyOn(api, 'createThingStock').mockRejectedValue(
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

    await renderStockThingScreen([], props, contextValue)

    await userEvent.type(screen.getByLabelText('Prix *'), '20')
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

  it('should display error for virtual offer without url', async () => {
    vi.spyOn(api, 'createThingStock').mockRejectedValue({
      message: 'oups',
      name: 'ApiError',
      body: { url: 'broken virtual offer !' },
    })

    await renderStockThingScreen([], props, contextValue)

    await userEvent.type(screen.getByLabelText('Prix *'), '20')
    await userEvent.click(
      screen.getByRole('button', { name: 'Enregistrer et continuer' })
    )

    expect(
      screen.getByText(
        'Vous n’avez pas renseigné l’URL d’accès à l’offre dans la page Informations pratiques.'
      )
    ).toBeInTheDocument()
  })

  describe('activation codes', () => {
    it('should submit activation codes and freeze quantity when a csv is provided', async () => {
      vi.spyOn(api, 'createThingStock').mockResolvedValue({
        id: 12,
      })
      props.offer = {
        ...offer,
        isDigital: true,
      }
      await renderStockThingScreen([], props, contextValue)

      const button = screen.getByRole('button', {
        name: "Ajouter des codes d'activation",
      })
      await userEvent.click(button)

      const uploadButton = screen.getByText(
        'Importer un fichier .csv depuis l’ordinateur'
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
      expect(
        screen.getByLabelText('Quantité', {
          exact: false,
        })
      ).toBeDisabled()

      const priceInput = screen.getByLabelText('Prix *')
      await userEvent.clear(priceInput)
      await userEvent.type(priceInput, '14.01')
      const expirationInput = screen.getByLabelText("Date d'expiration *")
      expect(expirationInput).toBeDisabled()
      const date = new Date()
      expect(expirationInput).toHaveValue(today)
      await userEvent.click(screen.getByText('Enregistrer et continuer'))
      // TEST
      expect(api.createThingStock).toHaveBeenCalledWith({
        offerId: offer.id,

        bookingLimitDatetime: null,
        price: 14.01,
        quantity: 5,
        activationCodes: ['ABH', 'JHB', 'IOP', 'KLM', 'MLK'],
        activationCodesExpirationDatetime: serializeThingBookingLimitDatetime(
          date,
          '75'
        ),
      })
    })

    it('should display an error when activation code file is incorrect', async () => {
      vi.spyOn(api, 'createThingStock').mockResolvedValue({
        id: 12,
      })
      props.offer = {
        ...offer,
        isDigital: true,
      }
      await renderStockThingScreen([], props, contextValue)

      const button = screen.getByRole('button', {
        name: "Ajouter des codes d'activation",
      })
      await userEvent.click(button)

      const uploadButton = await screen.findByText(
        'Importer un fichier .csv depuis l’ordinateur'
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
          'Une erreur s’est produite lors de l’import de votre fichier.'
        )
      ).resolves.toBeInTheDocument()

      await userEvent.click(
        screen.getByRole('button', { name: 'Fermer la fenêtre modale' })
      )
      expect(title).not.toBeInTheDocument()
    })

    it('should display an expiration field disabled when activationCodesExpirationDatetime is provided', async () => {
      props.offer = {
        ...offer,
        isDigital: true,
      }
      await renderStockThingScreen(
        [
          getOfferStockFactory({
            bookingsQuantity: 1,
            price: 12,
            hasActivationCode: true,
            activationCodesExpirationDatetime: '2020-12-15T12:00:00Z',
          }),
        ],
        props,
        contextValue
      )

      expect(
        screen.getByRole('spinbutton', {
          name: 'Quantité',
        })
      ).toBeDisabled()
      const expirationInput = screen.getByLabelText("Date d'expiration *")
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
      await renderStockThingScreen([], props, contextValue)

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
      await renderStockThingScreen([], props, contextValue)

      const quantityInput = screen.getByLabelText('Quantité')
      await userEvent.type(quantityInput, value)
      await userEvent.tab()
      expect(quantityInput).toHaveValue(expectedNumber)
    }
  )

  it('should not block when going outside and form is not touched', async () => {
    vi.spyOn(api, 'createThingStock').mockResolvedValue({
      id: 12,
    })

    await renderStockThingScreen([], props, contextValue)

    await userEvent.click(screen.getByText('Go outside !'))

    expect(screen.getByText('This is outside stock form')).toBeInTheDocument()
  })

  it('should be able to stay on stock form after click on "Rester sur la page"', async () => {
    vi.spyOn(api, 'createThingStock').mockResolvedValue({
      id: 12,
    })

    await renderStockThingScreen([], props, contextValue)
    await userEvent.type(
      screen.getByLabelText('Quantité', {
        exact: false,
      }),
      '20'
    )
    await userEvent.tab()

    await userEvent.click(screen.getByText('Go outside !'))

    await userEvent.click(screen.getByText('Rester sur la page'))

    expect(screen.getByTestId('stock-thing-form')).toBeInTheDocument()
  })

  it('should be able to quit without submitting from RouteLeavingGuard', async () => {
    vi.spyOn(api, 'createThingStock').mockResolvedValue({
      id: 12,
    })

    await renderStockThingScreen([], props, contextValue)
    await userEvent.type(
      screen.getByLabelText('Quantité', {
        exact: false,
      }),
      '20'
    )

    await userEvent.click(screen.getByText('Go outside !'))
    expect(
      screen.getByText('Les informations non enregistrées seront perdues')
    ).toBeInTheDocument()

    await userEvent.click(screen.getByText('Quitter la page'))
    expect(api.createThingStock).not.toHaveBeenCalled()

    expect(screen.getByText('This is outside stock form')).toBeInTheDocument()
  })

  it('should log an event when the limit date is updated', async () => {
    await renderStockThingScreen(
      [
        getOfferStockFactory({
          bookingLimitDatetime: '2020-12-15',
        }),
      ],
      props,
      contextValue
    )

    const input = screen.getByLabelText('Date limite de réservation')
    await waitFor(() => expect(input).toHaveValue('2020-12-15'))
    await userEvent.clear(input)
    await userEvent.click(screen.getByLabelText('Prix *'))

    expect(mockLogEvent).toHaveBeenCalledWith(
      Events.UPDATED_BOOKING_LIMIT_DATE,
      expect.objectContaining({ bookingLimitDatetime: '' })
    )
  })

  it('should not log an event when the limit date is updated but the value is the same as the initial value', async () => {
    await renderStockThingScreen(
      [
        getOfferStockFactory({
          bookingLimitDatetime: '2020-12-15',
        }),
      ],
      props,
      contextValue
    )

    const input = screen.getByLabelText('Date limite de réservation')
    await waitFor(() => expect(input).toHaveValue('2020-12-15'))
    await userEvent.clear(input)
    await userEvent.type(input, '2020-12-15')
    await userEvent.click(screen.getByLabelText('Prix *'))
    expect(mockLogEvent).not.toHaveBeenCalled()
  })
})
