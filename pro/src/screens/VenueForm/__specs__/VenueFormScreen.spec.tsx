import '@testing-library/jest-dom'

import { render, screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { createMemoryHistory } from 'history'
import React from 'react'
import { Provider } from 'react-redux'
import { Router } from 'react-router'

import { api } from 'apiClient/api'
import { ApiError, SharedCurrentUserResponseModel } from 'apiClient/v1'
import { ApiRequestOptions } from 'apiClient/v1/core/ApiRequestOptions'
import { ApiResult } from 'apiClient/v1/core/ApiResult'
import Notification from 'components/layout/Notification/Notification'
import { IOfferer } from 'core/Offerers/types'
import { IVenue } from 'core/Venue'
import { IVenueFormValues } from 'new_components/VenueForm'
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
  const history = createMemoryHistory()
  render(
    <Provider
      store={configureTestStore({
        user: {
          initialized: true,
          currentUser,
        },
      })}
    >
      <Router history={history}>
        <VenueFormScreen
          initialValues={initialValues}
          isCreatingVenue={isCreatingVenue}
          offerer={{ id: 'AE' } as IOfferer}
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
  return { history }
}
jest.mock('apiClient/api', () => ({
  api: {
    postCreateVenue: jest.fn(),
    editVenue: jest.fn(),
  },
}))

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
  mail: 'em@ail.fr',
  name: 'MINISTERE DE LA CULTURE',
  publicName: 'Melodie Sims',
  siret: '881 457 238 23022',
  venueType: 'GAMES',
  venueLabel: 'BM',
  departmentCode: '',
  address: 'PARIS',
  additionalAddress: '',
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
  isWithdrawalAppliedOnAllOffers: false,
  reimbursementPointId: 91,
}

describe('screen | VenueForm', () => {
  describe('Navigation', () => {
    it('administrators should be redirected to the list of structures after creating a venue', async () => {
      const { history } = renderForm(
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

      await userEvent.click(screen.getByText('Valider'))

      await waitFor(() => {
        expect(history.location.pathname).toBe('/structures/AE')
      })
    })

    it('non administrators should be redirected to home page after creating a venue', async () => {
      const { history } = renderForm(
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

      await userEvent.click(screen.getByText('Valider'))

      await waitFor(() => {
        expect(history.location.pathname).toBe('/accueil')
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

      await userEvent.click(screen.getByText('Valider'))

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
        undefined
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

      await userEvent.click(screen.getByText('Valider'))

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

      jest.spyOn(api, 'postCreateVenue').mockRejectedValue({})

      await userEvent.click(screen.getByText('Valider'))

      await waitFor(() => {
        expect(
          screen.getByText('Erreur inconnue lors de la sauvegarde du lieu.')
        ).toBeInTheDocument()
      })
    })
  })
})
