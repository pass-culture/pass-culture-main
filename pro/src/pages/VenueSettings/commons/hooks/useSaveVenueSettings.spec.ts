import { act, renderHook } from '@testing-library/react'
import React from 'react'
import { useForm } from 'react-hook-form'
import { Provider } from 'react-redux'
import * as reactRouter from 'react-router'
import { describe, expect, it, vi } from 'vitest'

import type { ApiRequestOptions } from '@/apiClient/adage/core/ApiRequestOptions'
import type { ApiResult } from '@/apiClient/adage/core/ApiResult'
import { ApiError } from '@/apiClient/v1'
import * as useAnalytics from '@/app/App/analytics/firebase'
import { Events } from '@/commons/core/FirebaseEvents/constants'
import * as useNotification from '@/commons/hooks/useNotification'
import { configureTestStore } from '@/commons/store/testUtils'
import { defaultGetVenue } from '@/commons/utils/factories/collectiveApiFactories'

import type {
  VenueSettingsFormContext,
  VenueSettingsFormValues,
} from '../types'
import { saveVenueSettings } from '../utils/saveVenueSettings'
import { useSaveVenueSettings } from './useSaveVenueSettings'

vi.mock('react-router', async () => {
  const actual =
    await vi.importActual<typeof import('react-router')>('react-router')
  return {
    ...actual,
    useNavigate: vi.fn(),
    useLocation: vi.fn(),
  }
})

vi.mock('../utils/saveVenueSettings', () => ({
  saveVenueSettings: vi.fn(() => Promise.resolve()),
}))

const defaultFormValues: VenueSettingsFormValues = {
  bookingEmail: 'contact@lieuexemple.com',
  comment: '',
  name: '',
  publicName: '',
  siret: '12345678901234',
  venueSiret: 12345678901234,
  venueType: 'Théâtre',
  withdrawalDetails:
    "Les retraits sont autorisés jusqu'à 24 heures avant l'événement.",
  manuallySetAddress: false,
  addressAutocomplete: '123 Rue Principale, Ville Exemple',
  banId: '12345',
  city: 'Ville Exemple',
  latitude: '48.8566',
  longitude: '2.3522',
  coords: '48.8566, 2.3522',
  postalCode: '75001',
  inseeCode: '75111',
  'search-addressAutocomplete': '123 Rue Principale, Ville Exemple',
  street: '123 Rue Principale',
}

const defaultFormContext: VenueSettingsFormContext = {
  isCaledonian: false,
  withSiret: true,
  isVenueVirtual: false,
  siren: '12345678901234',
}

const renderUseSaveVenueSettings = (params: {
  venue: typeof defaultGetVenue
}) => {
  const formValues = {
    ...defaultFormValues,
  }
  const formContext = {
    ...defaultFormContext,
  }

  const store = configureTestStore()
  const wrapper: React.FC<{ children?: React.ReactNode }> = ({ children }) =>
    React.createElement(Provider, { store, children })

  return renderHook(
    ({ venue }) => {
      const form = useForm<VenueSettingsFormValues>({
        context: formContext,
        defaultValues: formValues,
      })
      const save = useSaveVenueSettings({ form, venue })
      return { form, formContext, ...save }
    },
    {
      initialProps: params,
      wrapper,
    }
  )
}

describe('useSaveVenueSettings', () => {
  const useLocationMockReturnValue: reactRouter.Location = {
    hash: '',
    key: '',
    pathname: '/lieux/id',
    search: '',
    state: {},
  }

  const logEvent = vi.fn()

  const notifyError = vi.fn()
  const notifySuccess = vi.fn()

  beforeEach(async () => {
    vi.clearAllMocks()

    const notifsImport = (await vi.importActual(
      '@/commons/hooks/useNotification'
    )) as ReturnType<typeof useNotification.useNotification>
    vi.spyOn(useNotification, 'useNotification').mockImplementation(() => ({
      ...notifsImport,
      success: notifySuccess,
      error: notifyError,
    }))

    const analyticsImport = (await vi.importActual(
      '@/app/App/analytics/firebase'
    )) as ReturnType<typeof useAnalytics.useAnalytics>
    vi.spyOn(useAnalytics, 'useAnalytics').mockImplementation(() => ({
      ...analyticsImport,
      logEvent: logEvent,
    }))
  })

  it('should early navigate + success when form not dirty', async () => {
    vi.mocked(reactRouter.useLocation).mockReturnValue(
      useLocationMockReturnValue
    )
    const useNavigateMock = vi.fn()
    vi.spyOn(reactRouter, 'useNavigate').mockReturnValue(useNavigateMock)

    const venue = {
      ...defaultGetVenue,
    }

    const { result } = renderUseSaveVenueSettings({ venue })
    await act(async () => {
      await result.current.saveAndContinue(
        result.current.form.getValues(),
        result.current.formContext
      )
    })

    expect(saveVenueSettings).toHaveBeenCalled()
    // SWR mutate not asserted (real SWR not mocked)
    expect(useNavigateMock).toHaveBeenCalledWith(
      expect.stringMatching(
        `/structures/${venue.managingOfferer.id}/lieux/${venue.id}$`
      )
    )
    expect(notifySuccess).toHaveBeenCalled()
    expect(logEvent).toHaveBeenCalled()
  })

  it('should notify error when save functions throw', async () => {
    vi.spyOn(reactRouter, 'useLocation').mockReturnValue(
      useLocationMockReturnValue
    )
    const useNavigateMock = vi.fn()
    vi.spyOn(reactRouter, 'useNavigate').mockReturnValue(useNavigateMock)
    vi.mocked(saveVenueSettings).mockRejectedValueOnce(new Error('boom'))

    const venue = {
      ...defaultGetVenue,
    }

    const { result } = renderUseSaveVenueSettings({ venue })

    act(() => {
      result.current.form.setValue('siret', '')
    })

    await act(async () => {
      await result.current.saveAndContinue(
        result.current.form.getValues(),
        result.current.formContext
      )
    })

    expect(notifyError).toHaveBeenCalledWith(
      'Erreur lors de la sauvegarde de la structure.'
    )
    expect(useNavigateMock).not.toHaveBeenCalled()
    expect(logEvent).toHaveBeenCalledWith(Events.CLICKED_SAVE_VENUE, {
      from: '/lieux/id',
      saved: false,
      isEdition: true,
    })
  })

  it('should set the form with api error', async () => {
    vi.spyOn(reactRouter, 'useLocation').mockReturnValue(
      useLocationMockReturnValue
    )

    vi.mocked(saveVenueSettings).mockRejectedValueOnce(
      new ApiError(
        {} as ApiRequestOptions,
        {
          status: 400,
          body: {
            siret: ['Veuillez renseigner un SIRET'],
          },
        } as ApiResult,
        ''
      )
    )

    const venue = {
      ...defaultGetVenue,
    }

    const { result } = renderUseSaveVenueSettings({ venue })

    const spyFormSetError = vi.spyOn(result.current.form, 'setError')

    await act(async () => {
      await result.current.saveAndContinue(
        result.current.form.getValues(),
        result.current.formContext
      )
    })

    expect(spyFormSetError).toHaveBeenCalledWith('siret', {
      type: 'siret',
      message: 'Veuillez renseigner un SIRET',
    })
  })
})
