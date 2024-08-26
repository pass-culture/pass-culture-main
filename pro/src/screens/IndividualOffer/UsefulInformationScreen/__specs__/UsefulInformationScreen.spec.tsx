import { screen, waitFor, within } from '@testing-library/react'
import { userEvent } from '@testing-library/user-event'

import { api } from 'apiClient/api'
import {
  IndividualOfferContext,
  IndividualOfferContextValues,
} from 'context/IndividualOfferContext/IndividualOfferContext'
import { CATEGORY_STATUS } from 'core/Offers/constants'
import {
  categoryFactory,
  getIndividualOfferFactory,
  individualOfferContextValuesFactory,
  subcategoryFactory,
  venueListItemFactory,
} from 'utils/individualApiFactories'
import {
  renderWithProviders,
  RenderWithProvidersOptions,
} from 'utils/renderWithProviders'
import { sharedCurrentUserFactory } from 'utils/storeFactories'

import {
  UsefulInformationScreen,
  UsefulInformationScreenProps,
} from '../UsefulInformationScreen'

const renderUsefulInformationScreen = (
  props: UsefulInformationScreenProps,
  contextValue: IndividualOfferContextValues,
  options: RenderWithProvidersOptions = {}
) => {
  return renderWithProviders(
    <IndividualOfferContext.Provider value={contextValue}>
      <UsefulInformationScreen {...props} />
    </IndividualOfferContext.Provider>,
    {
      user: sharedCurrentUserFactory(),
      ...options,
    }
  )
}

vi.mock('apiClient/api', () => ({
  api: {
    getVenues: vi.fn().mockResolvedValue({
      venues: [],
    }),
    patchOffer: vi.fn(),
  },
}))

describe('screens:IndividualOffer::UsefulInformation', () => {
  let props: UsefulInformationScreenProps
  let contextValue: IndividualOfferContextValues

  beforeEach(() => {
    const categories = [
      categoryFactory({
        id: 'A',
        proLabel: 'Catégorie A',
        isSelectable: true,
      }),
    ]
    const subCategories = [
      subcategoryFactory({
        id: 'virtual',
        categoryId: 'A',
        proLabel: 'Sous catégorie online de A',
        isEvent: false,
        canBeDuo: false,
        onlineOfflinePlatform: CATEGORY_STATUS.ONLINE,
      }),
      subcategoryFactory({
        id: 'physical',
        categoryId: 'A',
        proLabel: 'Sous catégorie offline de A',
        isEvent: false,
        conditionalFields: ['ean'],
        canBeDuo: true,
        canBeEducational: false,
        canBeWithdrawable: false,
        onlineOfflinePlatform: CATEGORY_STATUS.OFFLINE,
      }),
    ]

    props = {
      offer: getIndividualOfferFactory({
        id: 3,
      }),
    }

    contextValue = individualOfferContextValuesFactory({
      categories,
      subCategories,
    })
  })

  it('should render the component', async () => {
    renderUsefulInformationScreen(props, contextValue)
    expect(
      await screen.findByRole('heading', { name: 'Retrait de l’offre' })
    ).toBeInTheDocument()

    const withdrawalDetails = await screen.findByTestId(
      'wrapper-withdrawalDetails'
    )
    expect(withdrawalDetails).toBeInTheDocument()

    expect(
      within(withdrawalDetails).getByText('Informations de retrait')
    ).toBeInTheDocument()

    expect(
      await screen.findByRole('heading', { name: 'Modalités d’accessibilité' })
    ).toBeInTheDocument()

    expect(
      await screen.findByRole('heading', { name: 'Notifications' })
    ).toBeInTheDocument()
  })

  it('should display offer location if venue is physical and WIP_ENABLE_OFFER_ADDRESS is active', async () => {
    vi.spyOn(api, 'getVenues').mockResolvedValue({
      venues: [
        {
          ...venueListItemFactory({
            id: 3,
            publicName: 'Lieu Nom Public Pour Test',
          }),
          address: {
            banId: '75101_9575_00003',
            city: 'Paris',
            id: 945,
            id_oa: 1,
            inseeCode: '75056',
            isEditable: false,
            isManualEdition: false,
            label: 'MINISTERE DE LA CULTURE',
            latitude: 48.87171,
            longitude: 2.30829,
            postalCode: '75001',
            street: '3 Rue de Valois',
          },
        },
      ],
    })

    renderUsefulInformationScreen(props, contextValue, {
      features: ['WIP_ENABLE_OFFER_ADDRESS'],
    })

    // Block should be visible at this point
    expect(
      await screen.findByRole('heading', { name: 'Localisation de l’offre' })
    ).toBeInTheDocument()

    // If user chooses the venue address (OA)...
    await userEvent.click(
      screen.getByRole('radio', { name: /Lieu Nom Public Pour Test/ })
    )
    // ...then he shouldn't see the other fields to provide a label and an address
    expect(
      screen.queryByLabelText(/Intitulé de la localisation/)
    ).not.toBeInTheDocument()

    // If user chooses to check another address...
    await userEvent.click(
      screen.getByRole('radio', { name: /À une autre adresse/ })
    )
    // ...then he should see the other fields to provide a label and an address
    expect(
      screen.queryByLabelText(/Intitulé de la localisation/)
    ).toBeInTheDocument()
  })

  it('should submit the form with correct payload', async () => {
    vi.spyOn(api, 'patchOffer').mockResolvedValue(
      getIndividualOfferFactory({
        id: 12,
      })
    )

    renderUsefulInformationScreen(props, contextValue)

    await waitFor(async () => {
      await userEvent.type(
        screen.getByLabelText(/Informations de retrait/),
        'My information'
      )
      await userEvent.click(screen.getByLabelText(/Visuel/))
      await userEvent.click(screen.getByLabelText(/Psychique ou cognitif/))

      await userEvent.click(screen.getByText('Enregistrer les modifications'))
    })

    expect(api.patchOffer).toHaveBeenCalledOnce()
    expect(api.patchOffer).toHaveBeenCalledWith(3, {
      audioDisabilityCompliant: true,
      bookingContact: undefined,
      bookingEmail: null,
      description: undefined,
      durationMinutes: undefined,
      extraData: undefined,
      isDuo: undefined,
      isNational: true,
      mentalDisabilityCompliant: false,
      motorDisabilityCompliant: true,
      name: undefined,
      shouldSendMail: false,
      url: undefined,
      visualDisabilityCompliant: false,
      withdrawalDelay: undefined,
      withdrawalDetails: 'My information',
      withdrawalType: undefined,
    })
  })
})
