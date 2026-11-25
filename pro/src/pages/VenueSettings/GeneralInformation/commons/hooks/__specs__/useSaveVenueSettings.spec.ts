import { act, renderHook } from '@testing-library/react'
import React from 'react'
import { useForm } from 'react-hook-form'
import { Provider } from 'react-redux'
import * as reactRouter from 'react-router'
import { describe, expect, it, vi } from 'vitest'

import { api } from '@/apiClient/api'
import type { ApiRequestOptions, ApiResult } from '@/apiClient/compat'
import { ApiError } from '@/apiClient/compat'
import * as useAnalytics from '@/app/App/analytics/firebase'
import { Events } from '@/commons/core/FirebaseEvents/constants'
import * as useSnackBar from '@/commons/hooks/useSnackBar'
import * as useSyncVenueCacheModule from '@/commons/hooks/useSyncVenueCache'
import { configureTestStore } from '@/commons/store/testUtils'
import { defaultGetVenue } from '@/commons/utils/factories/collectiveApiFactories'

import type {
  VenueSettingsFormContext,
  VenueSettingsFormValues,
} from '../../types'
import { useSaveVenueSettings } from '../useSaveVenueSettings'

vi.mock('@/apiClient/api', () => ({
  api: {
    editVenue: vi.fn(),
  },
}))

vi.mock('react-router', async () => {
  const actual =
    await vi.importActual<typeof import('react-router')>('react-router')
  return {
    ...actual,
    useNavigate: vi.fn(),
    useLocation: vi.fn(),
  }
})

const defaultFormValues: VenueSettingsFormValues = {
  comment: '',
  name: '',
  publicName: '',
  siret: '12345678901234',
  venueSiret: 12345678901234,
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
  isOpenToPublic: 'true',
  accessibility: {
    visual: true,
    mental: false,
    audio: false,
    motor: false,
    none: false,
  },
  isAccessibilityAppliedOnAllOffers: false,
}

const defaultFormContext: VenueSettingsFormContext = {
  isCaledonian: false,
  withSiret: true,
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

  const snackBarError = vi.fn()
  const snackBarSuccess = vi.fn()
  const syncVenueWithData = vi.fn()

  beforeEach(async () => {
    const snackBarsImport = (await vi.importActual(
      '@/commons/hooks/useSnackBar'
    )) as ReturnType<typeof useSnackBar.useSnackBar>
    vi.spyOn(useSnackBar, 'useSnackBar').mockImplementation(() => ({
      ...snackBarsImport,
      success: snackBarSuccess,
      error: snackBarError,
    }))

    const analyticsImport = (await vi.importActual(
      '@/app/App/analytics/firebase'
    )) as ReturnType<typeof useAnalytics.useAnalytics>
    vi.spyOn(useAnalytics, 'useAnalytics').mockImplementation(() => ({
      ...analyticsImport,
      logEvent: logEvent,
    }))

    vi.spyOn(useSyncVenueCacheModule, 'useSyncVenueCache').mockReturnValue({
      syncVenue: vi.fn(),
      syncVenueWithData,
    })
  })

  it('should patch venue settings and notify success', async () => {
    vi.mocked(reactRouter.useLocation).mockReturnValue(
      useLocationMockReturnValue
    )
    const useNavigateMock = vi.fn()
    vi.spyOn(reactRouter, 'useNavigate').mockReturnValue(useNavigateMock)

    const venue = {
      ...defaultGetVenue,
    }
    vi.mocked(api.editVenue).mockResolvedValueOnce(venue)

    const { result } = renderUseSaveVenueSettings({ venue })
    await act(async () => {
      await result.current.save(
        result.current.form.getValues(),
        result.current.formContext
      )
    })

    expect(api.editVenue).toHaveBeenCalledWith({
      path: { venue_id: Number(venue.id) },
      body: {
        activity: undefined,
        banId: '12345',
        city: 'Ville Exemple',
        comment: '',
        culturalDomains: undefined,
        description: undefined,
        inseeCode: '75111',
        isManualEdition: false,
        isOpenToPublic: true,
        latitude: 48.8566,
        longitude: 2.3522,
        name: '',
        postalCode: '75001',
        publicName: '',
        siret: '12345678901234',
        street: '123 Rue Principale',
        withdrawalDetails:
          "Les retraits sont autorisés jusqu'à 24 heures avant l'événement.",
      },
    })
    expect(syncVenueWithData).toHaveBeenCalledWith(venue.id, venue)
    expect(snackBarSuccess).toHaveBeenCalledWith(
      'Vos modifications ont été sauvegardées'
    )
    expect(logEvent).toHaveBeenCalledWith(Events.CLICKED_SAVE_VENUE, {
      saved: true,
      isEdition: true,
    })
  })

  it('should notify error when the API request fails', async () => {
    vi.spyOn(reactRouter, 'useLocation').mockReturnValue(
      useLocationMockReturnValue
    )
    const useNavigateMock = vi.fn()
    vi.spyOn(reactRouter, 'useNavigate').mockReturnValue(useNavigateMock)
    vi.mocked(api.editVenue).mockRejectedValueOnce(new Error('boom'))

    const venue = {
      ...defaultGetVenue,
    }

    const { result } = renderUseSaveVenueSettings({ venue })

    act(() => {
      result.current.form.setValue('siret', '')
    })

    await act(async () => {
      await result.current.save(
        result.current.form.getValues(),
        result.current.formContext
      )
    })

    expect(snackBarError).toHaveBeenCalledWith(
      'Erreur lors de la sauvegarde de la structure.'
    )
    expect(useNavigateMock).not.toHaveBeenCalled()
    expect(logEvent).toHaveBeenCalledWith(Events.CLICKED_SAVE_VENUE, {
      saved: false,
      isEdition: true,
    })
  })

  it('should set the form with api error', async () => {
    vi.spyOn(reactRouter, 'useLocation').mockReturnValue(
      useLocationMockReturnValue
    )

    vi.mocked(api.editVenue).mockRejectedValueOnce(
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
      await result.current.save(
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
