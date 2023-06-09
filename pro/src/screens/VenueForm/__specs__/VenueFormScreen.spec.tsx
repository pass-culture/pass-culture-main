import { screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import fetch from 'jest-fetch-mock'
import React from 'react'
import { Route, Routes } from 'react-router-dom'

import { apiAdresse } from 'apiClient/adresse'
import { api } from 'apiClient/api'
import {
  ApiError,
  EditVenueBodyModel,
  GetVenueResponseModel,
  SharedCurrentUserResponseModel,
  VenueTypeCode,
} from 'apiClient/v1'
import { ApiRequestOptions } from 'apiClient/v1/core/ApiRequestOptions'
import { ApiResult } from 'apiClient/v1/core/ApiResult'
import Notification from 'components/Notification/Notification'
import { IVenueFormValues } from 'components/VenueForm'
import { IOfferer } from 'core/Offerers/types'
import { IVenue } from 'core/Venue'
import * as useNewOfferCreationJourney from 'hooks/useNewOfferCreationJourney'
import { defaultCollectiveDmsApplication } from 'utils/collectiveApiFactories'
import { renderWithProviders } from 'utils/renderWithProviders'

import { VenueFormScreen } from '../index'

const venueTypes: SelectOption[] = [
  { value: 'ARTISTIC_COURSE', label: 'Cours et pratique artistiques' },
  { value: 'SCIENTIFIC_CULTURE', label: 'Culture scientifique' },
]

const venueLabels: SelectOption[] = [
  { value: 'AE', label: 'Architecture contemporaine remarquable' },
  {
    value: 'A9',
    label: "CAC - Centre d'art contemporain d'int\u00e9r\u00eat national",
  },
]

const renderForm = (
  currentUser: SharedCurrentUserResponseModel,
  initialValues: IVenueFormValues,
  isCreatingVenue: boolean,
  venue?: IVenue | undefined,
  features?: { list: { isActive: true; nameKey: string }[] },
  hasBookingQuantity?: boolean
) => {
  const storeOverrides = {
    user: {
      initialized: true,
      currentUser,
    },
    features: features,
  }

  renderWithProviders(
    <>
      <Routes>
        <Route
          path="/structures/AE/lieux/creation"
          element={
            <>
              <VenueFormScreen
                initialValues={initialValues}
                isCreatingVenue={isCreatingVenue}
                offerer={{ id: 'AE', siren: '881457238' } as IOfferer}
                venueTypes={venueTypes}
                venueLabels={venueLabels}
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
    { storeOverrides, initialRouterEntries: ['/structures/AE/lieux/creation'] }
  )
}

const mockNavigate = jest.fn()
jest.mock('react-router-dom', () => ({
  ...jest.requireActual('react-router-dom'),
  useNavigate: () => mockNavigate,
}))

jest.mock('apiClient/api', () => ({
  api: {
    postCreateVenue: jest.fn(),
    getSiretInfo: jest.fn(),
    editVenue: jest.fn(),
    getEducationalPartners: jest.fn(),
    getAvailableReimbursementPoints: jest.fn(),
    canOffererCreateEducationalOffer: jest.fn(),
  },
}))
jest.spyOn(api, 'getEducationalPartners').mockResolvedValue({ partners: [] })

jest.spyOn(api, 'getAvailableReimbursementPoints').mockResolvedValue([])

jest.spyOn(api, 'getSiretInfo').mockResolvedValue({
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

jest.spyOn(api, 'canOffererCreateEducationalOffer').mockResolvedValue()

jest.mock('apiClient/adresse', () => {
  return {
    ...jest.requireActual('apiClient/adresse'),
    default: {
      getDataFromAddress: jest.fn(),
    },
  }
})

jest.spyOn(apiAdresse, 'getDataFromAddress').mockResolvedValue([
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

// Mock l'appel à https://api-adresse.data.gouv.fr/search/?limit=${limit}&q=${address}
// Appel fait dans apiAdresse.getDataFromAddress
fetch.mockResponse(
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

jest.mock('utils/windowMatchMedia', () => ({
  doesUserPreferReducedMotion: jest.fn().mockReturnValue(false),
}))

Element.prototype.scrollIntoView = jest.fn()

const venueResponse: GetVenueResponseModel = {
  hasPendingBankInformationApplication: false,
  demarchesSimplifieesApplicationId: '',
  collectiveDomains: [],
  dateCreated: '2022-02-02',
  fieldsUpdated: [],
  isVirtual: false,
  managingOffererId: '',
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
  id: 'id',
  isPermanent: true,
  latitude: 0,
  longitude: 0,
  bookingEmail: 'a@b.c',
  name: 'name',
  nonHumanizedId: 0,
  pricingPoint: null,
  postalCode: '75008',
  publicName: 'name',
  siret: '88145723823022',
  venueTypeCode: VenueTypeCode.COURS_ET_PRATIQUE_ARTISTIQUES,
  venueLabelId: 'AE',
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
    dateModifiedAtLastProvider: null,
    demarchesSimplifieesApplicationId: null,
    fieldsUpdated: [],
    id: 'id',
    nonHumanizedId: 1,
    idAtProviders: null,
    isValidated: true,
    lastProviderId: null,
    name: 'name',
    postalCode: 'string',
    siren: null,
  },
}

describe('screen | VenueForm', () => {
  let formValues: IVenueFormValues
  let expectedEditVenue: Partial<EditVenueBodyModel>
  let venue: IVenue
  beforeEach(() => {
    formValues = {
      bannerMeta: undefined,
      comment: '',
      description: '',
      isVenueVirtual: false,
      bookingEmail: 'em@ail.fr',
      name: 'MINISTERE DE LA CULTURE',
      publicName: 'Melodie Sims',
      siret: '88145723823022',
      venueType: 'GAMES',
      venueLabel: 'EM',
      departmentCode: '',
      address: 'PARIS',
      addressAutocomplete: 'Allee Rene Omnes 35400 Saint-Malo',
      'search-addressAutocomplete': 'PARIS',
      city: 'Saint-Malo',
      latitude: 48.635699,
      longitude: -2.006961,
      postalCode: '35400',
      accessibility: {
        visual: false,
        mental: true,
        audio: false,
        motor: true,
        none: false,
      },
      isAccessibilityAppliedOnAllOffers: false,
      phoneNumber: '0604855967',
      email: 'em@ail.com',
      webSite: 'https://www.site.web',
      isPermanent: false,
      id: undefined,
      bannerUrl: '',
      withdrawalDetails: 'withdrawal details field',
      venueSiret: null,
      isWithdrawalAppliedOnAllOffers: false,
      reimbursementPointId: 91,
    }

    venue = {
      hasPendingBankInformationApplication: false,
      demarchesSimplifieesApplicationId: '',
      collectiveDomains: [],
      dateCreated: '2022-02-02',
      fieldsUpdated: [],
      isVirtual: false,
      managingOffererId: '',
      accessibility: {
        visual: false,
        audio: false,
        motor: false,
        mental: false,
        none: true,
      },
      address: 'Address',
      bannerMeta: null,
      bannerUrl: '',
      city: 'city',
      comment: 'comment',
      contact: {
        email: 'email',
        phoneNumber: '0606060606',
        webSite: 'web',
      },
      description: 'description',
      departmentCode: '75008',
      dmsToken: '',
      id: 'id',
      isPermanent: true,
      isVenueVirtual: false,
      latitude: 0,
      longitude: 0,
      mail: 'a@b.c',
      name: 'name',
      nonHumanizedId: 15,
      pricingPoint: null,
      postalCode: '75008',
      publicName: 'name',
      siret: '88145723823022',
      venueType: 'ARTISTIC_COURSE',
      venueLabel: 'AE',
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
        dateModifiedAtLastProvider: null,
        demarchesSimplifieesApplicationId: null,
        fieldsUpdated: [],
        id: 'id',
        nonHumanizedId: 1,
        idAtProviders: null,
        isValidated: true,
        lastProviderId: null,
        name: 'name',
        postalCode: 'string',
        siren: null,
      },
      hasAdageId: false,
      adageInscriptionDate: null,
      collectiveDmsApplication: null,
    }
  })
  describe('Navigation', () => {
    describe('With new offer creation journey', () => {
      beforeEach(() => {
        jest.spyOn(useNewOfferCreationJourney, 'default').mockReturnValue(true)
      })

      it('User should be redirected with the new creation journey', async () => {
        jest.spyOn(api, 'postCreateVenue').mockResolvedValue({ id: '56' })
        renderForm(
          {
            id: 'EY',
            isAdmin: true,
          } as SharedCurrentUserResponseModel,
          formValues,
          true,
          undefined
        )

        await userEvent.click(screen.getByText(/Enregistrer et créer le lieu/))
        await waitFor(() => {
          expect(
            screen.getByText('Vos modifications ont bien été enregistrées')
          ).toBeInTheDocument()
        })
      })

      it('User should be redirected with the creation popin displayed', async () => {
        renderForm(
          {
            id: 'EY',
            isAdmin: false,
          } as SharedCurrentUserResponseModel,
          formValues,
          true,
          undefined
        )
        jest.spyOn(api, 'postCreateVenue').mockResolvedValue({ id: '56' })

        await userEvent.click(screen.getByText(/Enregistrer et créer le lieu/))

        await waitFor(() => {
          expect(
            screen.queryByText('Vos modifications ont bien été enregistrées')
          ).not.toBeInTheDocument()
        })
      })
    })

    it('User should be redirected to the edit page after creating a venue', async () => {
      renderForm(
        {
          id: 'EY',
          isAdmin: true,
        } as SharedCurrentUserResponseModel,
        formValues,
        true,
        undefined
      )
      jest.spyOn(api, 'postCreateVenue').mockResolvedValue({ id: '56' })

      await userEvent.click(screen.getByText(/Enregistrer et continuer/))

      await waitFor(() => {
        expect(
          screen.getByText('Vos modifications ont bien été enregistrées')
        ).toBeInTheDocument()
      })
    })
  })

  describe('Errors displaying', () => {
    it('should display an error when the venue could not be created', async () => {
      renderForm(
        {
          id: 'EY',
          isAdmin: true,
        } as SharedCurrentUserResponseModel,
        formValues,
        true,
        undefined
      )

      jest.spyOn(api, 'postCreateVenue').mockRejectedValue(
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

    it('should display an error when the venue could not be updated', async () => {
      renderForm(
        {
          id: 'EY',
          isAdmin: true,
        } as SharedCurrentUserResponseModel,
        formValues,
        false,
        venue
      )

      jest.spyOn(api, 'editVenue').mockRejectedValue(
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

    it('Submit creation form that fails with unknown error', async () => {
      renderForm(
        {
          id: 'EY',
          isAdmin: true,
        } as SharedCurrentUserResponseModel,
        formValues,
        true,
        undefined
      )

      const postCreateVenue = jest
        .spyOn(api, 'postCreateVenue')
        .mockRejectedValue({})

      await userEvent.click(screen.getByText(/Enregistrer/))

      expect(postCreateVenue).toHaveBeenCalled()
      await waitFor(() => {
        expect(
          screen.getByText('Erreur inconnue lors de la sauvegarde du lieu.')
        ).toBeInTheDocument()
      })
    })

    it('should let update the virtual venue with limited fields', async () => {
      formValues.isVenueVirtual = true
      renderForm(
        {
          id: 'EY',
          isAdmin: true,
        } as SharedCurrentUserResponseModel,
        formValues,
        false,
        venue
      )

      const editVenue = jest
        .spyOn(api, 'editVenue')
        .mockResolvedValue(venueResponse)

      await userEvent.click(screen.getByText(/Enregistrer/))
      expect(editVenue).toHaveBeenCalledWith(15, { reimbursementPointId: 91 })
    })
  })

  it('should display error on submit for non virtual venues when adress is not selected from suggestions', async () => {
    formValues.addressAutocomplete = ''
    formValues.address = ''
    formValues.postalCode = ''
    formValues.departmentCode = ''

    renderForm(
      {
        id: 'EY',
        isAdmin: true,
      } as SharedCurrentUserResponseModel,
      formValues,
      false,
      venue
    )
    const adressInput = screen.getByLabelText('Adresse postale')

    await userEvent.type(adressInput, '12 rue des fleurs')
    await userEvent.click(screen.getByText(/Enregistrer/))

    expect(
      await screen.findByText(
        'Veuillez sélectionner une adresse parmi les suggestions'
      )
    ).toBeInTheDocument()
  })

  it('should not display error on submit when venue is virtual', async () => {
    formValues.isVenueVirtual = true
    renderForm(
      {
        id: 'EY',
        isAdmin: true,
      } as SharedCurrentUserResponseModel,
      formValues,
      false,
      venue
    )
    const adressInput = screen.getByLabelText('Adresse postale')

    await userEvent.type(adressInput, '12 rue des fleurs')
    await userEvent.click(screen.getByText(/Enregistrer/))

    expect(
      await screen.queryByText(
        'Veuillez sélectionner une adresse parmi les suggestions'
      )
    ).not.toBeInTheDocument()
  })

  describe('Displaying', () => {
    it('should diplay only some fields when the venue is virtual', async () => {
      venue.isVirtual = true

      renderForm(
        {
          id: 'EY',
          isAdmin: false,
        } as SharedCurrentUserResponseModel,
        formValues,
        false,
        venue
      )

      await waitFor(() => {
        expect(
          screen.queryByTestId('wrapper-publicName')
        ).not.toBeInTheDocument()
      })
      expect(screen.getByText('Type de lieu')).toBeInTheDocument()

      expect(screen.queryByText('Adresse du lieu')).not.toBeInTheDocument()
      expect(
        screen.queryByTestId('wrapper-description')
      ).not.toBeInTheDocument()
      expect(screen.queryByTestId('wrapper-venueLabel')).not.toBeInTheDocument()
      expect(
        screen.queryByText('Accessibilité du lieu')
      ).not.toBeInTheDocument()
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
  })

  describe('Displaying with new onboarding', () => {
    let features: { list: { isActive: true; nameKey: string }[] }

    beforeEach(() => {
      features = {
        list: [{ isActive: true, nameKey: 'WIP_ENABLE_NEW_ONBOARDING' }],
      }
    })

    it('should display new onboarding wording labels', async () => {
      venue.isVirtual = false
      renderForm(
        {
          id: 'EY',
          isAdmin: false,
        } as SharedCurrentUserResponseModel,
        formValues,
        false,
        venue,
        features
      )

      await waitFor(() => {
        expect(screen.queryByTestId('wrapper-publicName')).toBeInTheDocument()
      })

      expect(screen.getByText('Raison sociale')).toBeInTheDocument()
      expect(screen.getByText('Nom public')).toBeInTheDocument()
      expect(screen.getByText('Activité principale')).toBeInTheDocument()

      await waitFor(() => {
        expect(
          screen.getByText(
            'À remplir si différent de la raison sociale. En le remplissant, c’est ce dernier qui sera visible du public.'
          )
        ).toBeInTheDocument()
      })
    })

    it('should render errors on creation', async () => {
      formValues.venueType = ''
      formValues.name = ''
      formValues.publicName = ''
      renderForm(
        {
          id: 'EY',
          isAdmin: false,
        } as SharedCurrentUserResponseModel,
        formValues,
        true,
        undefined,
        features
      )

      await userEvent.click(screen.getByText(/Enregistrer et continuer/))

      expect(
        await screen.findByText(
          'Veuillez renseigner la raison sociale de votre lieu'
        )
      ).toBeInTheDocument()

      expect(
        screen.getByText('Veuillez sélectionner une activité principale')
      ).toBeInTheDocument()
    })
  })

  describe('Withdrawal dialog to send mail', () => {
    let features: { list: { isActive: true; nameKey: string }[] }

    beforeEach(() => {
      expectedEditVenue = {
        address: 'PARIS',
        audioDisabilityCompliant: false,
        bookingEmail: 'em@ail.fr',
        city: 'Saint-Malo',
        comment: '',
        contact: {
          email: 'em@ail.com',
          phoneNumber: '0604855967',
          socialMedias: null,
          website: 'https://www.site.web',
        },
        description: '',
        isEmailAppliedOnAllOffers: true,
        isAccessibilityAppliedOnAllOffers: false,
        latitude: 48.635699,
        longitude: -2.006961,
        mentalDisabilityCompliant: true,
        motorDisabilityCompliant: true,
        name: 'MINISTERE DE LA CULTURE',
        postalCode: '35400',
        publicName: 'Melodie Sims',
        reimbursementPointId: 91,
        shouldSendMail: false,
        siret: '88145723823022',
        venueTypeCode: 'GAMES',
        // @ts-expect-error string is not assignable to type number
        venueLabelId: 'EM',
        visualDisabilityCompliant: false,
        withdrawalDetails: 'Nouvelle information de retrait',
      }

      features = {
        list: [
          { isActive: true, nameKey: 'WIP_ENABLE_WITHDRAWAL_UPDATED_MAIL' },
        ],
      }
    })

    it('should display withdrawal and submit on confirm dialog button when offer has bookingQuantity and withdrawalDetails is updated and isWithdrawalAppliedOnAllOffers is true', async () => {
      renderForm(
        {
          id: 'EY',
          isAdmin: false,
        } as SharedCurrentUserResponseModel,
        formValues,
        false,
        venue,
        features,
        true
      )

      const editVenue = jest
        .spyOn(api, 'editVenue')
        .mockResolvedValue({ id: 'AA' } as GetVenueResponseModel)

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
        expect(
          screen.getByText('Vos modifications ont bien été enregistrées')
        ).toBeInTheDocument()
      })
    })

    it('should display withdrawal dialog and submit on cancel click and should not send mail', async () => {
      renderForm(
        {
          id: 'EY',
          isAdmin: false,
        } as SharedCurrentUserResponseModel,
        formValues,
        false,
        venue,
        features,
        true
      )

      const editVenue = jest
        .spyOn(api, 'editVenue')
        .mockResolvedValue({ id: 'AA' } as GetVenueResponseModel)

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

      await waitFor(() => {
        expect(
          screen.getByText('Vos modifications ont bien été enregistrées')
        ).toBeInTheDocument()
      })
    })

    it("should not display withdrawal if offer has no bookingQuantity or withdrawalDetails doesn't change or isWithdrawalAppliedOnAllOffers is not check", async () => {
      expectedEditVenue.isWithdrawalAppliedOnAllOffers = false

      renderForm(
        {
          id: 'EY',
          isAdmin: false,
        } as SharedCurrentUserResponseModel,
        formValues,
        false,
        venue,
        features,
        false
      )

      const editVenue = jest
        .spyOn(api, 'editVenue')
        .mockResolvedValue({ id: 'AA' } as GetVenueResponseModel)

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

      await waitFor(() => {
        expect(
          screen.getByText('Vos modifications ont bien été enregistrées')
        ).toBeInTheDocument()
      })
    })

    it('should close withdrawal dialog and not submit if user close dialog', async () => {
      renderForm(
        {
          id: 'EY',
          isAdmin: false,
        } as SharedCurrentUserResponseModel,
        formValues,
        false,
        venue,
        features,
        true
      )

      const editVenue = jest
        .spyOn(api, 'editVenue')
        .mockResolvedValue({ id: 'AA' } as GetVenueResponseModel)

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

      const closeWithdrawalDialogButton = await screen.getByRole('button', {
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
      renderForm(
        {
          id: 'EY',
          isAdmin: false,
        } as SharedCurrentUserResponseModel,
        formValues,
        false,
        venue,
        features,
        true
      )

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

  describe('EAC Section', () => {
    it('should display eac section if offerer is eligble to eac and ff active', async () => {
      renderForm(
        {
          id: 'EY',
          isAdmin: false,
        } as SharedCurrentUserResponseModel,
        formValues,
        false,
        {
          ...venue,
          hasAdageId: true,
        },
        {
          list: [
            { isActive: true, nameKey: 'WIP_ENABLE_COLLECTIVE_DMS_TRACKING' },
          ],
        }
      )
      await waitFor(
        () => expect(api.canOffererCreateEducationalOffer).toHaveBeenCalled
      )
      expect(
        screen.getByRole('heading', {
          name: 'Mes informations pour les enseignants',
        })
      ).toBeInTheDocument()
    })
    it('should display dms timeline if venue has dms application and ff active', async () => {
      jest
        .spyOn(api, 'canOffererCreateEducationalOffer')
        .mockRejectedValueOnce('error')
      renderForm(
        {
          id: 'EY',
          isAdmin: false,
        } as SharedCurrentUserResponseModel,
        formValues,
        false,
        {
          ...venue,
          hasAdageId: false,
          collectiveDmsApplication: { ...defaultCollectiveDmsApplication },
        },
        {
          list: [
            { isActive: true, nameKey: 'WIP_ENABLE_COLLECTIVE_DMS_TRACKING' },
          ],
        }
      )
      await waitFor(
        () => expect(api.canOffererCreateEducationalOffer).toHaveBeenCalled
      )
      expect(screen.getByText('Votre dossier a été déposé')).toBeInTheDocument()
    })

    it('should not display eac section if offerer is not eligble and has not dms application', async () => {
      jest
        .spyOn(api, 'canOffererCreateEducationalOffer')
        .mockRejectedValueOnce('error')
      renderForm(
        {
          id: 'EY',
          isAdmin: false,
        } as SharedCurrentUserResponseModel,
        formValues,
        false,
        {
          ...venue,
          hasAdageId: false,
        },
        {
          list: [
            { isActive: true, nameKey: 'WIP_ENABLE_COLLECTIVE_DMS_TRACKING' },
          ],
        }
      )
      await waitFor(
        () => expect(api.canOffererCreateEducationalOffer).toHaveBeenCalled
      )
      expect(
        screen.queryByRole('heading', {
          name: 'Mes informations pour les enseignants',
        })
      ).not.toBeInTheDocument()
    })
    it('should display eac section during venue creation if venue has siret and is eligible to eac', async () => {
      renderForm(
        {
          id: 'EY',
          isAdmin: false,
        } as SharedCurrentUserResponseModel,
        formValues,
        true,
        undefined,
        {
          list: [
            { isActive: true, nameKey: 'WIP_ENABLE_COLLECTIVE_DMS_TRACKING' },
          ],
        }
      )
      await waitFor(
        () => expect(api.canOffererCreateEducationalOffer).toHaveBeenCalled
      )
      expect(
        screen.queryByRole('heading', {
          name: 'Mes informations pour les enseignants',
        })
      ).toBeInTheDocument()
    })
  })
})
