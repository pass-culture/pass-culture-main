import { screen, within } from '@testing-library/react'
import { userEvent } from '@testing-library/user-event'
import { FormProvider, useForm } from 'react-hook-form'

import { api } from 'apiClient/api'
import { SubcategoryIdEnum, WithdrawalTypeEnum } from 'apiClient/v1'
import {
  IndividualOfferContext,
  IndividualOfferContextValues,
} from 'commons/context/IndividualOfferContext/IndividualOfferContext'
import { REIMBURSEMENT_RULES } from 'commons/core/Finances/constants'
import {
  CATEGORY_STATUS,
  OFFER_WIZARD_MODE,
} from 'commons/core/Offers/constants'
import { getAddressResponseIsLinkedToVenueModelFactory } from 'commons/utils/factories/commonOffersApiFactories'
import {
  categoryFactory,
  getIndividualOfferFactory,
  getOfferVenueFactory,
  individualOfferContextValuesFactory,
  subcategoryFactory,
  venueListItemFactory,
} from 'commons/utils/factories/individualApiFactories'
import { sharedCurrentUserFactory } from 'commons/utils/factories/storeFactories'
import {
  renderWithProviders,
  RenderWithProvidersOptions,
} from 'commons/utils/renderWithProviders'

import {
  IndividualOfferInformationsScreen,
  IndividualOfferInformationsScreenProps,
} from './IndividualOfferInformationsScreen'

function renderUsefulInformationScreen(
  defaultProps: IndividualOfferInformationsScreenProps,
  contextValue: IndividualOfferContextValues,
  options: RenderWithProvidersOptions = {}
) {
  const Wrapper = () => {
    const methods = useForm({
      defaultValues: {},
      mode: 'onBlur',
    })

    return (
      <FormProvider {...methods}>
        <IndividualOfferInformationsScreen {...defaultProps} />
      </FormProvider>
    )
  }

  options = {
    user: sharedCurrentUserFactory(),
    ...options,
  }

  renderWithProviders(
    <IndividualOfferContext.Provider value={contextValue}>
      <Wrapper />
    </IndividualOfferContext.Provider>,
    options
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
  let props: IndividualOfferInformationsScreenProps
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
        canBeWithdrawable: false,
        onlineOfflinePlatform: CATEGORY_STATUS.OFFLINE,
      }),
    ]

    props = {
      offer: getIndividualOfferFactory({
        id: 3,
        venue: getOfferVenueFactory({ id: 1 }),
      }),
    }

    contextValue = individualOfferContextValuesFactory({
      categories,
      subCategories,
    })

    vi.spyOn(api, 'getVenues').mockResolvedValue({
      venues: [
        {
          ...venueListItemFactory({
            id: 1,
            publicName: 'Lieu Nom Public Pour Test',
          }),
          address: {
            banId: '75101_9575_00003',
            city: 'Paris',
            id: 945,
            id_oa: 1,
            inseeCode: '75056',
            isLinkedToVenue: false,
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
      await screen.findByRole('heading', {
        name: 'Lien de réservation externe en l’absence de crédit',
      })
    ).toBeInTheDocument()

    expect(
      await screen.findByRole('heading', { name: 'Notifications' })
    ).toBeInTheDocument()
  })

  it('should display offer location if venue is physical', async () => {
    renderUsefulInformationScreen(props, contextValue)

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

    // If user toggle manual address fields
    await userEvent.click(
      screen.getByRole('button', {
        name: 'Vous ne trouvez pas votre adresse ?',
      })
    )
    // ...then he should see the different address fields
    expect(
      screen.queryByLabelText(/Adresse postale/, { selector: '#street' })
    ).toBeInTheDocument()
    expect(screen.queryByLabelText(/Code postal/)).toBeInTheDocument()
    expect(screen.queryByLabelText(/Ville/)).toBeInTheDocument()
    expect(screen.queryByLabelText(/Coordonnées GPS/)).toBeInTheDocument()
  })

  it('should submit the form with correct payload', async () => {
    vi.spyOn(api, 'patchOffer').mockResolvedValue(
      getIndividualOfferFactory({
        id: 12,
      })
    )
    renderUsefulInformationScreen(props, contextValue)

    const withdrawalField = await screen.findByLabelText(
      /Informations de retrait/
    )

    await userEvent.click(
      screen.getByRole('radio', {
        name: 'Lieu Nom Public Pour Test – 3 Rue de Valois 75001 Paris',
      })
    )
    await userEvent.type(withdrawalField, 'My information')
    await userEvent.click(screen.getByLabelText(/Visuel/))
    await userEvent.click(screen.getByLabelText(/Psychique ou cognitif/))
    await userEvent.click(screen.getByText('Enregistrer les modifications'))

    expect(api.patchOffer).toHaveBeenCalledOnce()
    expect(api.patchOffer).toHaveBeenCalledWith(3, {
      address: {
        city: 'Paris',
        isManualEdition: false,
        isVenueAddress: true,
        label: 'MINISTERE DE LA CULTURE',
        latitude: '48.87171',
        longitude: '2.30829',
        postalCode: '75001',
        street: '3 Rue de Valois',
        banId: '75101_9575_00003',
        inseeCode: '75056',
      },
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
      shouldSendMail: true,
      externalTicketOfficeUrl: 'https://chuck.no',
      url: undefined,
      visualDisabilityCompliant: false,
      withdrawalDelay: null,
      withdrawalDetails: 'My information',
      withdrawalType: WithdrawalTypeEnum.NO_TICKET,
    })
  })

  it('should display not reimbursed banner when subcategory is not reimbursed', async () => {
    renderUsefulInformationScreen(
      props,
      individualOfferContextValuesFactory({
        categories: [
          categoryFactory({
            id: 'A',
            isSelectable: true,
          }),
        ],
        subCategories: [
          subcategoryFactory({
            categoryId: 'A',
            // should be same as subcategoryId in offer
            id: SubcategoryIdEnum.SEANCE_CINE,
            reimbursementRule: REIMBURSEMENT_RULES.NOT_REIMBURSED,
          }),
        ],
      })
    )
    expect(
      await screen.findByText('Cette offre numérique ne sera pas remboursée.')
    ).toBeInTheDocument()
    expect(
      screen.queryByText(
        'Quelles sont les offres numériques éligibles au remboursement ?'
      )
    ).toHaveAttribute(
      'href',
      'https://aide.passculture.app/hc/fr/articles/6043184068252'
    )
  })

  it('should disabled all fields if another offer with the same EAN is already published', async () => {
    renderUsefulInformationScreen(
      props,
      individualOfferContextValuesFactory({
        publishedOfferWithSameEAN: getIndividualOfferFactory(),
      })
    )

    const withdrawalField = await screen.findByRole('textbox', {
      name: 'Informations de retrait',
    })

    expect(withdrawalField).toBeDisabled()
  })

  describe('ConfirmDialog', () => {
    beforeEach(() => {
      // Should appear only in edition mode, and if offer has pending bookings
      vi.mock('commons/hooks/useOfferWizardMode', () => ({
        useOfferWizardMode: vi.fn(() => OFFER_WIZARD_MODE.EDITION),
      }))
      props.offer.hasPendingBookings = true
    })

    afterEach(() => {
      vi.resetAllMocks()
      props.offer.hasPendingBookings = false
    })

    it('should display the dialog if user updated withdrawal informations', async () => {
      renderUsefulInformationScreen(props, contextValue)

      const withdrawalInformationsField = await screen.findByRole('textbox', {
        name: /Informations de retrait/,
      })

      await userEvent.type(withdrawalInformationsField, 'Update retrait')

      await userEvent.click(
        await screen.findByRole('button', {
          name: /Enregistrer les modifications/,
        })
      )

      expect(
        screen.getByText(
          /Les changements vont s’appliquer à l’ensemble des réservations en cours associées/
        )
      ).toBeInTheDocument()

      expect(
        screen.getByText('Vous avez modifié les modalités de retrait.')
      ).toBeInTheDocument()
    })

    it('should display the dialog if user updated address field(s)', async () => {
      const propsWithOfferAddress = structuredClone(props)
      propsWithOfferAddress.offer.address =
        getAddressResponseIsLinkedToVenueModelFactory({
          id: 666,
          id_oa: 1337,
          isLinkedToVenue: false,
          isManualEdition: true,
        })

      renderUsefulInformationScreen(propsWithOfferAddress, contextValue)

      const cityField = await screen.findByRole('textbox', {
        name: /Ville/,
      })

      await userEvent.type(cityField, 'Updated city')

      await userEvent.click(
        await screen.findByRole('button', {
          name: /Enregistrer les modifications/,
        })
      )

      expect(
        screen.getByText(
          /Les changements vont s’appliquer à l’ensemble des réservations en cours associées/
        )
      ).toBeInTheDocument()

      expect(
        screen.getByText('Vous avez modifié la localisation.')
      ).toBeInTheDocument()
    })

    it('should display the dialog if user updated both withdrawalInformations and address field(s)', async () => {
      const propsWithOfferAddress = structuredClone(props)
      propsWithOfferAddress.offer.address =
        getAddressResponseIsLinkedToVenueModelFactory({
          id: 666,
          id_oa: 1337,
          isLinkedToVenue: false,
          isManualEdition: true,
        })

      renderUsefulInformationScreen(propsWithOfferAddress, contextValue)

      const withdrawalInformationsField = await screen.findByRole('textbox', {
        name: /Informations de retrait/,
      })
      const cityField = await screen.findByRole('textbox', {
        name: /Ville/,
      })

      await userEvent.type(cityField, 'Updated city')
      await userEvent.type(withdrawalInformationsField, 'Update retrait')

      await userEvent.click(
        await screen.findByRole('button', {
          name: /Enregistrer les modifications/,
        })
      )

      expect(
        screen.getByText(
          /Les changements vont s’appliquer à l’ensemble des réservations en cours associées/
        )
      ).toBeInTheDocument()

      expect(
        screen.getByText(
          'Vous avez modifié les modalités de retrait et la localisation.'
        )
      ).toBeInTheDocument()
    })

    it('should NOT display the dialog if offer has no pending bookings', async () => {
      props.offer.hasPendingBookings = false

      vi.spyOn(api, 'patchOffer').mockResolvedValue(
        getIndividualOfferFactory({
          id: 12,
        })
      )

      renderUsefulInformationScreen(props, contextValue)

      const withdrawalInformationsField = await screen.findByRole('textbox', {
        name: /Informations de retrait/,
      })

      await userEvent.type(withdrawalInformationsField, 'Update retrait')

      await userEvent.click(
        await screen.findByRole('button', {
          name: /Enregistrer les modifications/,
        })
      )

      expect(
        screen.queryByText(
          /Les changements vont s’appliquer à l’ensemble des réservations en cours associées/
        )
      ).not.toBeInTheDocument()

      expect(api.patchOffer).toHaveBeenCalledOnce()
    })
  })
})
