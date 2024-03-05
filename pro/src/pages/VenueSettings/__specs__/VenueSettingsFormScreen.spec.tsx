import { screen, waitFor } from '@testing-library/react'
import { userEvent } from '@testing-library/user-event'
import React from 'react'
import { Route, Routes } from 'react-router-dom'
import createFetchMock from 'vitest-fetch-mock'

import { apiAdresse } from 'apiClient/adresse'
import { api } from 'apiClient/api'
import {
  ApiError,
  EditVenueBodyModel,
  GetVenueResponseModel,
  VenueTypeCode,
} from 'apiClient/v1'
import { ApiRequestOptions } from 'apiClient/v1/core/ApiRequestOptions'
import { ApiResult } from 'apiClient/v1/core/ApiResult'
import Notification from 'components/Notification/Notification'
import { PATCH_SUCCESS_MESSAGE } from 'core/shared'
import { SelectOption } from 'custom_types/form'
import { defaultGetOffererResponseModel } from 'utils/apiFactories'
import { defaultGetVenue } from 'utils/collectiveApiFactories'
import { renderWithProviders } from 'utils/renderWithProviders'

import { VenueSettingsFormValues } from '../types'
import { VenueSettingsFormScreen } from '../VenueSettingsScreen'

const fetchMock = createFetchMock(vi)
fetchMock.enableMocks()

const venueLabels: SelectOption[] = [
  { value: '13', label: 'Architecture contemporaine remarquable' },
  {
    value: '14',
    label: "CAC - Centre d'art contemporain d’int\u00e9r\u00eat national",
  },
]

const venueTypes: SelectOption[] = [
  { value: 'ARTISTIC_COURSE', label: 'Cours et pratique artistiques' },
  { value: 'SCIENTIFIC_CULTURE', label: 'Culture scientifique' },
]

const renderForm = (
  initialValues: VenueSettingsFormValues,
  venue: GetVenueResponseModel,
  isAdmin = false,
  hasBookingQuantity?: boolean,
  features: string[] = []
) => {
  const storeOverrides = {
    user: {
      initialized: true,
      currentUser: {
        id: 'user_id',
        isAdmin,
      },
    },
  }

  renderWithProviders(
    <>
      <Routes>
        <Route
          path="/structures/AE/lieux/creation"
          element={
            <>
              <VenueSettingsFormScreen
                initialValues={initialValues}
                offerer={{
                  ...defaultGetOffererResponseModel,
                  id: 12,
                  siren: '881457238',
                }}
                venueLabels={venueLabels}
                venueTypes={venueTypes}
                providers={[]}
                venue={venue}
                venueProviders={[]}
                hasBookingQuantity={hasBookingQuantity}
              />
            </>
          }
        />
        <Route
          path="/structures/AE/lieux/:venueId"
          element={
            <>
              <div>Lieu créé</div>
            </>
          }
        />
      </Routes>
      <Notification />
    </>,
    {
      storeOverrides,
      initialRouterEntries: ['/structures/AE/lieux/creation'],
      features,
    }
  )
}

vi.mock('apiClient/api', () => ({
  api: {
    postCreateVenue: vi.fn(),
    getSiretInfo: vi.fn(),
    editVenue: vi.fn(),
    getEducationalPartners: vi.fn(() => Promise.resolve({ partners: [] })),
    getAvailableReimbursementPoints: vi.fn(() => Promise.resolve([])),
    canOffererCreateEducationalOffer: vi.fn(),
  },
}))
vi.spyOn(api, 'getSiretInfo').mockResolvedValue({
  active: true,
  address: {
    city: 'paris',
    postalCode: '75008',
    street: 'rue de paris',
  },
  name: 'lieu',
  siret: '88145723823022',
  ape_code: '95.07A',
  legal_category_code: '1000',
})

vi.spyOn(api, 'canOffererCreateEducationalOffer').mockResolvedValue({
  canCreate: true,
})

vi.mock('apiClient/adresse', async () => {
  return {
    ...((await vi.importActual('apiClient/adresse')) ?? {}),
    default: {
      getDataFromAddress: vi.fn(),
    },
  }
})

vi.spyOn(apiAdresse, 'getDataFromAddress').mockResolvedValue([
  {
    address: '12 rue des lilas',
    city: 'Lyon',
    id: '1',
    latitude: 11.1,
    longitude: -11.1,
    label: '12 rue des lilas 69002 Lyon',
    postalCode: '69002',
  },
  {
    address: '12 rue des tournesols',
    city: 'Paris',
    id: '2',
    latitude: 22.2,
    longitude: -2.22,
    label: '12 rue des tournesols 75003 Paris',
    postalCode: '75003',
  },
])

// Mock l’appel à https://api-adresse.data.gouv.fr/search/?limit=${limit}&q=${address}
// Appel fait dans apiAdresse.getDataFromAddress
fetchMock.mockResponse(
  JSON.stringify({
    features: [
      {
        properties: {
          name: 'name',
          city: 'city',
          id: 'id',
          label: 'label',
          postcode: 'postcode',
        },
        geometry: {
          coordinates: [0, 0],
        },
      },
    ],
  }),
  { status: 200 }
)

vi.mock('utils/windowMatchMedia', () => ({
  doesUserPreferReducedMotion: vi.fn(),
}))

Element.prototype.scrollIntoView = vi.fn()

vi.mock('core/Venue/siretApiValidate', () => ({
  default: () => Promise.resolve(),
}))

const venueResponse: GetVenueResponseModel = {
  hasPendingBankInformationApplication: false,
  demarchesSimplifieesApplicationId: '',
  collectiveDomains: [],
  dateCreated: '2022-02-02',
  isVirtual: false,
  visualDisabilityCompliant: false,
  audioDisabilityCompliant: false,
  motorDisabilityCompliant: false,
  mentalDisabilityCompliant: false,
  address: 'Address',
  bannerMeta: null,
  bannerUrl: '',
  city: 'city',
  comment: 'comment',
  contact: {
    email: 'email',
    phoneNumber: '0606060606',
    website: 'web',
  },
  description: 'description',
  departementCode: '75008',
  dmsToken: 'dms-token-12345',
  isPermanent: true,
  latitude: 0,
  longitude: 0,
  bookingEmail: 'a@b.c',
  name: 'name',
  id: 0,
  pricingPoint: null,
  postalCode: '75008',
  publicName: 'name',
  siret: '88145723823022',
  timezone: 'Europe/Paris',
  venueTypeCode: VenueTypeCode.COURS_ET_PRATIQUE_ARTISTIQUES,
  venueLabelId: 1,
  reimbursementPointId: 0,
  withdrawalDetails: 'string',
  collectiveAccessInformation: 'string',
  collectiveDescription: 'string',
  collectiveEmail: 'string',
  collectiveInterventionArea: [],
  collectiveLegalStatus: null,
  collectiveNetwork: [],
  collectivePhone: 'string',
  collectiveStudents: [],
  collectiveWebsite: 'string',
  adageInscriptionDate: null,
  hasAdageId: false,
  collectiveDmsApplications: [],
  managingOfferer: {
    address: null,
    city: 'string',
    dateCreated: 'string',
    demarchesSimplifieesApplicationId: null,
    id: 1,
    isValidated: true,
    name: 'name',
    postalCode: 'string',
    siren: null,
  },
}

describe('VenueFormScreen', () => {
  let formValues: VenueSettingsFormValues
  let expectedEditVenue: Partial<EditVenueBodyModel>
  let venue: GetVenueResponseModel

  beforeEach(() => {
    formValues = {
      comment: '',
      bookingEmail: 'em@ail.fr',
      name: 'MINISTERE DE LA CULTURE',
      publicName: 'Melodie Sims',
      siret: '88145723823022',
      venueType: VenueTypeCode.JEUX_JEUX_VID_OS,
      address: 'PARIS',
      banId: '35288_7283_00001',
      addressAutocomplete: 'Allee Rene Omnes 35400 Saint-Malo',
      'search-addressAutocomplete': 'PARIS',
      city: 'Saint-Malo',
      latitude: 48.635699,
      longitude: -2.006961,
      postalCode: '35400',
      withdrawalDetails: 'withdrawal details field',
      venueSiret: null,
      venueLabel: '13',
      isWithdrawalAppliedOnAllOffers: false,
      reimbursementPointId: 91,
    }

    venue = {
      ...defaultGetVenue,
      hasPendingBankInformationApplication: false,
      demarchesSimplifieesApplicationId: '',
      collectiveDomains: [],
      dateCreated: '2022-02-02',
      isVirtual: false,
      address: 'Address',
      banId: 'ban_id',
      bannerMeta: null,
      bannerUrl: '',
      city: 'city',
      comment: 'comment',
      contact: {
        email: 'email',
        phoneNumber: '0606060606',
        website: 'web',
      },
      description: 'description',
      departementCode: '75008',
      dmsToken: '',
      isPermanent: true,
      latitude: 0,
      longitude: 0,
      name: 'name',
      id: 15,
      pricingPoint: null,
      postalCode: '75008',
      publicName: 'name',
      siret: '88145723823022',
      reimbursementPointId: 0,
      withdrawalDetails: 'string',
      collectiveAccessInformation: 'string',
      collectiveDescription: 'string',
      collectiveEmail: 'string',
      collectiveInterventionArea: [],
      collectiveLegalStatus: null,
      collectiveNetwork: [],
      collectivePhone: 'string',
      collectiveStudents: [],
      collectiveWebsite: 'string',
      managingOfferer: {
        address: null,
        city: 'string',
        dateCreated: 'string',
        demarchesSimplifieesApplicationId: null,
        id: 1,
        isValidated: true,
        name: 'name',
        postalCode: 'string',
        siren: null,
      },
      hasAdageId: false,
      adageInscriptionDate: null,
      bankAccount: null,
    }
  })

  it('should display an error when the venue could not be updated', async () => {
    renderForm(formValues, venue)

    vi.spyOn(api, 'editVenue').mockRejectedValue(
      new ApiError(
        {} as ApiRequestOptions,
        {
          body: {
            siret: ['ensure this value has at least 14 characters'],
          },
        } as ApiResult,
        ''
      )
    )

    await userEvent.click(screen.getByText(/Enregistrer/))

    await waitFor(() => {
      expect(
        screen.getByText('ensure this value has at least 14 characters')
      ).toBeInTheDocument()
    })
  })

  it('should let update the virtual venue with limited fields', async () => {
    renderForm(formValues, venue)

    const editVenue = vi
      .spyOn(api, 'editVenue')
      .mockResolvedValue(venueResponse)

    await userEvent.click(screen.getByText(/Enregistrer/))
    expect(editVenue).toHaveBeenCalledWith(
      15,
      expect.objectContaining({ reimbursementPointId: 91 })
    )
  })

  it('should let update venue without siret', async () => {
    formValues.siret = ''
    formValues.comment = 'comment'
    const testedVenue = {
      ...venue,
      siret: null,
    }

    renderForm(formValues, testedVenue)

    const editVenue = vi
      .spyOn(api, 'editVenue')
      .mockResolvedValue(venueResponse)

    await userEvent.click(screen.getByText(/Enregistrer/))

    expect(editVenue).toHaveBeenCalled()
    expect(editVenue).not.toHaveBeenCalledWith(15, { siret: '' })
  })

  it('should display error on submit for non virtual venues when adress is not selected from suggestions', async () => {
    formValues.addressAutocomplete = ''
    formValues.address = ''
    formValues.postalCode = ''

    renderForm(formValues, venue)
    const adressInput = screen.getByLabelText('Adresse postale *')

    await userEvent.type(adressInput, '12 rue des fleurs')
    await userEvent.click(screen.getByText(/Enregistrer/))

    expect(
      await screen.findByText(
        'Veuillez sélectionner une adresse parmi les suggestions'
      )
    ).toBeInTheDocument()
  })

  it('should not display error on submit when venue is virtual', async () => {
    renderForm(formValues, venue)

    const adressInput = screen.getByLabelText('Adresse postale *')

    await userEvent.type(adressInput, '12 rue des fleurs')
    await userEvent.click(screen.getByText(/Enregistrer/))

    expect(
      screen.queryByText(
        'Veuillez sélectionner une adresse parmi les suggestions'
      )
    ).not.toBeInTheDocument()
  })

  it('should diplay only some fields when the venue is virtual', async () => {
    venue.isVirtual = true

    renderForm(formValues, venue, false)

    await waitFor(() => {
      expect(screen.queryByTestId('wrapper-publicName')).not.toBeInTheDocument()
    })
    expect(screen.getByText('Activité principale *')).toBeInTheDocument()

    expect(screen.queryByText('Adresse du lieu')).not.toBeInTheDocument()
    expect(screen.queryByTestId('wrapper-description')).not.toBeInTheDocument()
    expect(screen.queryByTestId('wrapper-venueLabel')).not.toBeInTheDocument()
    expect(screen.queryByText('Accessibilité du lieu')).not.toBeInTheDocument()
    expect(
      screen.queryByText('Informations de retrait de vos offres')
    ).not.toBeInTheDocument()
    expect(screen.queryByText('Contact')).not.toBeInTheDocument()
    expect(
      screen.queryByText(
        'Cette adresse s’appliquera par défaut à toutes vos offres, vous pourrez la modifier à l’échelle de chaque offre.'
      )
    ).not.toBeInTheDocument()
  })

  describe('Displaying with new onboarding', () => {
    it('should display new onboarding wording labels', async () => {
      venue.isVirtual = false
      renderForm(formValues, venue, false)

      await waitFor(() => {
        expect(screen.queryByTestId('wrapper-publicName')).toBeInTheDocument()
      })

      expect(screen.getByText('Raison sociale *')).toBeInTheDocument()
      expect(screen.getByText('Nom public')).toBeInTheDocument()
      expect(screen.getByText('Activité principale *')).toBeInTheDocument()

      await waitFor(() => {
        expect(
          screen.getByText(
            'À remplir si différent de la raison sociale. En le remplissant, c’est ce dernier qui sera visible du public.'
          )
        ).toBeInTheDocument()
      })
    })
  })

  describe('Withdrawal dialog to send mail', () => {
    beforeEach(() => {
      expectedEditVenue = {
        address: 'PARIS',
        banId: '35288_7283_00001',
        bookingEmail: 'em@ail.fr',
        city: 'Saint-Malo',
        comment: '',
        isEmailAppliedOnAllOffers: true,
        latitude: 48.635699,
        longitude: -2.006961,
        name: 'MINISTERE DE LA CULTURE',
        postalCode: '35400',
        publicName: 'Melodie Sims',
        reimbursementPointId: 91,
        shouldSendMail: false,
        siret: '88145723823022',
        venueTypeCode: VenueTypeCode.JEUX_JEUX_VID_OS,
        venueLabelId: 13,
        withdrawalDetails: 'Nouvelle information de retrait',
      }
    })

    it('should display withdrawal and submit on confirm dialog button when offer has bookingQuantity and withdrawalDetails is updated and isWithdrawalAppliedOnAllOffers is true', async () => {
      renderForm(formValues, venue, true, true)

      const editVenue = vi
        .spyOn(api, 'editVenue')
        .mockResolvedValue({ ...defaultGetVenue, id: 1 })

      await waitFor(() => {
        expect(
          screen.getByText('Informations de retrait de vos offres')
        ).toBeInTheDocument()
      })

      const withdrawalDetailsField = screen.getByDisplayValue(
        'withdrawal details field'
      )

      await userEvent.click(withdrawalDetailsField)
      await userEvent.clear(withdrawalDetailsField)
      await userEvent.type(
        withdrawalDetailsField,
        'Nouvelle information de retrait'
      )
      await waitFor(() => {
        expect(screen.getByText('Nouvelle information de retrait'))
      })
      venue.withdrawalDetails = 'Nouvelle information de retrait'

      await userEvent.click(
        screen.getByText(
          'Appliquer le changement à toutes les offres déjà existantes'
        )
      )
      expectedEditVenue.shouldSendMail = true
      expectedEditVenue.isWithdrawalAppliedOnAllOffers = true

      await userEvent.click(screen.getByText(/Enregistrer et quitter/))
      expect(
        await screen.findByText(
          'Souhaitez-vous prévenir les bénéficiaires de la modification des modalités de retrait ?'
        )
      ).toBeInTheDocument()

      const sendMailButton = await screen.findByText('Envoyer un email')
      await userEvent.click(sendMailButton)
      expect(
        screen.queryByText(
          'Souhaitez-vous prévenir les bénéficiaires de la modification des modalités de retrait ?'
        )
      ).not.toBeInTheDocument()

      expect(editVenue).toHaveBeenCalledWith(15, expectedEditVenue)

      await waitFor(() => {
        expect(screen.getByText(PATCH_SUCCESS_MESSAGE)).toBeInTheDocument()
      })
    })

    it('should display withdrawal dialog and submit on cancel click and should not send mail', async () => {
      renderForm(formValues, venue, false, true)

      const editVenue = vi
        .spyOn(api, 'editVenue')
        .mockResolvedValue({ ...defaultGetVenue, id: 1 })

      await waitFor(() => {
        expect(
          screen.getByText('Informations de retrait de vos offres')
        ).toBeInTheDocument()
      })

      const withdrawalDetailsField = screen.getByDisplayValue(
        'withdrawal details field'
      )

      await userEvent.click(withdrawalDetailsField)
      await userEvent.clear(withdrawalDetailsField)
      await userEvent.type(
        withdrawalDetailsField,
        'Nouvelle information de retrait'
      )
      await waitFor(() => {
        expect(screen.getByText('Nouvelle information de retrait'))
      })
      venue.withdrawalDetails = 'Nouvelle information de retrait'

      await userEvent.click(
        screen.getByText(
          'Appliquer le changement à toutes les offres déjà existantes'
        )
      )
      expectedEditVenue.isWithdrawalAppliedOnAllOffers = true

      await userEvent.click(screen.getByText(/Enregistrer et quitter/))

      expect(
        await screen.findByText(
          'Souhaitez-vous prévenir les bénéficiaires de la modification des modalités de retrait ?'
        )
      ).toBeInTheDocument()

      const cancelDialogButton = await screen.findByText('Ne pas envoyer')
      await userEvent.click(cancelDialogButton)
      await waitFor(() => {
        expect(
          screen.queryByText(
            'Souhaitez-vous prévenir les bénéficiaires de la modification des modalités de retrait ?'
          )
        ).not.toBeInTheDocument()
      })

      expect(editVenue).toHaveBeenCalledWith(15, expectedEditVenue)
    })

    it("should not display withdrawal if offer has no bookingQuantity or withdrawalDetails doesn't change or isWithdrawalAppliedOnAllOffers is not check", async () => {
      expectedEditVenue.isWithdrawalAppliedOnAllOffers = false

      renderForm(formValues, venue, false)

      const editVenue = vi
        .spyOn(api, 'editVenue')
        .mockResolvedValue({ ...defaultGetVenue, id: 1 })

      await waitFor(() => {
        expect(
          screen.getByText('Informations de retrait de vos offres')
        ).toBeInTheDocument()
      })

      const withdrawalDetailsField = screen.getByDisplayValue(
        'withdrawal details field'
      )

      await userEvent.click(withdrawalDetailsField)
      await userEvent.clear(withdrawalDetailsField)
      await userEvent.type(
        withdrawalDetailsField,
        'Nouvelle information de retrait'
      )
      await waitFor(() => {
        expect(screen.getByText('Nouvelle information de retrait'))
      })
      venue.withdrawalDetails = 'Nouvelle information de retrait'

      await userEvent.click(screen.getByText(/Enregistrer et quitter/))
      expect(editVenue).toHaveBeenCalledWith(15, expectedEditVenue)
    })

    it('should close withdrawal dialog and not submit if user close dialog', async () => {
      renderForm(formValues, venue, false, true)

      const editVenue = vi
        .spyOn(api, 'editVenue')
        .mockResolvedValue({ ...defaultGetVenue, id: 1 })

      await waitFor(() => {
        expect(
          screen.getByText('Informations de retrait de vos offres')
        ).toBeInTheDocument()
      })

      const withdrawalDetailsField = screen.getByDisplayValue(
        'withdrawal details field'
      )

      await userEvent.click(withdrawalDetailsField)
      await userEvent.clear(withdrawalDetailsField)
      await userEvent.type(
        withdrawalDetailsField,
        'Nouvelle information de retrait'
      )
      await waitFor(() => {
        expect(screen.getByText('Nouvelle information de retrait'))
      })
      venue.withdrawalDetails = 'Nouvelle information de retrait'

      await userEvent.click(
        screen.getByText(
          'Appliquer le changement à toutes les offres déjà existantes'
        )
      )
      expectedEditVenue.isWithdrawalAppliedOnAllOffers = true

      await userEvent.click(screen.getByText(/Enregistrer et quitter/))

      expect(
        await screen.findByText(
          'Souhaitez-vous prévenir les bénéficiaires de la modification des modalités de retrait ?'
        )
      ).toBeInTheDocument()

      const closeWithdrawalDialogButton = screen.getByRole('button', {
        name: 'Fermer la modale',
      })
      await userEvent.click(closeWithdrawalDialogButton)

      expect(
        screen.queryByText(
          'Souhaitez-vous prévenir les bénéficiaires de la modification des modalités de retrait ?'
        )
      ).not.toBeInTheDocument()

      expect(editVenue).toHaveBeenCalledTimes(0)
    })

    it('should not display withdrawal dialog if withdrawalDetails value after update is the same', async () => {
      renderForm(formValues, venue, false)

      await waitFor(() => {
        expect(
          screen.getByText('Informations de retrait de vos offres')
        ).toBeInTheDocument()
      })

      const withdrawalDetailsField = screen.getByDisplayValue(
        'withdrawal details field'
      )

      await userEvent.click(withdrawalDetailsField)
      await userEvent.clear(withdrawalDetailsField)
      await userEvent.type(withdrawalDetailsField, 'withdrawal details field')
      await waitFor(() => {
        expect(screen.getByText('withdrawal details field'))
      })
      await userEvent.click(
        screen.getByText(
          'Appliquer le changement à toutes les offres déjà existantes'
        )
      )
      expectedEditVenue.isWithdrawalAppliedOnAllOffers = true

      await userEvent.click(screen.getByText(/Enregistrer et quitter/))
      expect(
        screen.queryByText(
          'Souhaitez-vous prévenir les bénéficiaires de la modification des modalités de retrait ?'
        )
      ).not.toBeInTheDocument()
    })
  })
})
