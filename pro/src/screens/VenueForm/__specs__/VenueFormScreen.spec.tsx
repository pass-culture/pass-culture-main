import '@testing-library/jest-dom'

import { render, screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { createMemoryHistory } from 'history'
import fetch from 'jest-fetch-mock'
import React from 'react'
import { Provider } from 'react-redux'
import { Router } from 'react-router'

import { apiAdresse } from 'apiClient/adresse'
import { api } from 'apiClient/api'
import { ApiError, SharedCurrentUserResponseModel } from 'apiClient/v1'
import { ApiRequestOptions } from 'apiClient/v1/core/ApiRequestOptions'
import { ApiResult } from 'apiClient/v1/core/ApiResult'
import Notification from 'components/Notification/Notification'
import { IVenueFormValues } from 'components/VenueForm'
import { IOfferer } from 'core/Offerers/types'
import { IVenue } from 'core/Venue'
import * as useNewOfferCreationJourney from 'hooks/useNewOfferCreationJourney'
import { configureTestStore } from 'store/testUtils'

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
  venue?: IVenue | undefined
) => {
  render(
    <Provider
      store={configureTestStore({
        user: {
          initialized: true,
          currentUser,
        },
      })}
    >
      <Router history={createMemoryHistory()}>
        <VenueFormScreen
          initialValues={initialValues}
          isCreatingVenue={isCreatingVenue}
          offerer={{ id: 'AE', siren: '881457238' } as IOfferer}
          venueTypes={venueTypes}
          venueLabels={venueLabels}
          providers={[]}
          venue={venue}
          venueProviders={[]}
        />
      </Router>
      <Notification />
    </Provider>
  )
}
jest.mock('apiClient/api', () => ({
  api: {
    postCreateVenue: jest.fn(),
    getSiretInfo: jest.fn(),
    editVenue: jest.fn(),
    getEducationalPartners: jest.fn(),
    getAvailableReimbursementPoints: jest.fn(),
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
})

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

jest.mock('react-router-dom', () => ({
  ...jest.requireActual('react-router-dom'),
  useParams: () => ({
    offererId: 'AE',
  }),
}))

jest.mock('utils/windowMatchMedia', () => ({
  doesUserPreferReducedMotion: jest.fn().mockReturnValue(false),
}))

Element.prototype.scrollIntoView = jest.fn()

const formValues: IVenueFormValues = {
  bannerMeta: undefined,
  comment: '',
  description: '',
  isVenueVirtual: false,
  bookingEmail: 'em@ail.fr',
  name: 'MINISTERE DE LA CULTURE',
  publicName: 'Melodie Sims',
  siret: '88145723823022',
  venueType: 'GAMES',
  venueLabel: 'BM',
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
  id: '',
  bannerUrl: '',
  withdrawalDetails: 'Oui',
  venueSiret: null,
  isWithdrawalAppliedOnAllOffers: false,
  reimbursementPointId: 91,
}

const venue: IVenue = {
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
  nonHumanizedId: 0,
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
    bic: null,
    city: 'string',
    dateCreated: 'string',
    dateModifiedAtLastProvider: null,
    demarchesSimplifieesApplicationId: null,
    fieldsUpdated: [],
    iban: null,
    id: 'id',
    idAtProviders: null,
    isValidated: true,
    lastProviderId: null,
    name: 'name',
    postalCode: 'string',
    siren: null,
  },
}

describe('screen | VenueForm', () => {
  describe('Navigation', () => {
    describe('With new offer creation journey', () => {
      beforeEach(() => {
        jest.spyOn(useNewOfferCreationJourney, 'default').mockReturnValue(true)
      })

      it('User should be redirected with the new creation journey', async () => {
        renderForm(
          {
            id: 'EY',
            isAdmin: true,
            publicName: 'USER',
          } as SharedCurrentUserResponseModel,
          formValues,
          true,
          undefined
        )
        jest.spyOn(api, 'postCreateVenue').mockResolvedValue({ id: '56' })

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
            publicName: 'USER',
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
          publicName: 'USER',
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
          publicName: 'USER',
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

      expect(
        screen.getByText('ensure this value has at least 14 characters')
      ).toBeInTheDocument()
    })

    it('should display an error when the venue could not be updated', async () => {
      renderForm(
        {
          id: 'EY',
          isAdmin: true,
          publicName: 'USER',
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

      expect(
        screen.getByText('ensure this value has at least 14 characters')
      ).toBeInTheDocument()
    })

    it('Submit creation form that fails with unknown error', async () => {
      renderForm(
        {
          id: 'EY',
          isAdmin: true,
          publicName: 'USER',
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
          publicName: 'USER',
        } as SharedCurrentUserResponseModel,
        formValues,
        false,
        venue
      )

      const editVenue = jest.spyOn(api, 'editVenue').mockResolvedValue(venue)

      await userEvent.click(screen.getByText(/Enregistrer/))
      expect(editVenue).toHaveBeenCalledWith('id', { reimbursementPointId: 91 })
    })
  })

  describe('Displaying', () => {
    it('should diplay only some fields when the venue is virtual', async () => {
      venue.isVirtual = true

      renderForm(
        {
          id: 'EY',
          isAdmin: false,
          publicName: 'USER',
        } as SharedCurrentUserResponseModel,
        formValues,
        false,
        venue
      )

      expect(screen.queryByTestId('wrapper-publicName')).not.toBeInTheDocument()
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
})
