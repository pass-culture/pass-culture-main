import { act, renderHook } from '@testing-library/react'
import React from 'react'
import { useForm } from 'react-hook-form'
import { Provider } from 'react-redux'

import { apiNew } from '@/apiClient/api'
import type { ApiRequestOptions, ApiResult } from '@/apiClient/compat'
import { ApiError } from '@/apiClient/compat'
import * as useAnalytics from '@/app/App/analytics/firebase'
import { Events } from '@/commons/core/FirebaseEvents/constants'
import * as useSnackBar from '@/commons/hooks/useSnackBar'
import * as useSyncVenueCacheModule from '@/commons/hooks/useSyncVenueCache'
import { configureTestStore } from '@/commons/store/testUtils'
import { defaultGetVenue } from '@/commons/utils/factories/collectiveApiFactories'

import type { VenueSettingsNotificationsFormValues } from '../../schemas'
import { useSave } from '../useSave'

vi.mock('@/apiClient/api', () => ({
  apiNew: {
    editVenue: vi.fn(),
  },
}))

const defaultFormValues: VenueSettingsNotificationsFormValues = {
  bookingEmail: 'old@example.com',
}

const renderUseSave = (
  params: { venue: typeof defaultGetVenue } = { venue: defaultGetVenue }
) => {
  const store = configureTestStore()
  const wrapper: React.FC<{ children?: React.ReactNode }> = ({ children }) =>
    React.createElement(Provider, { store, children })

  return renderHook(
    ({ venue }) => {
      const form = useForm<VenueSettingsNotificationsFormValues>({
        defaultValues: defaultFormValues,
      })
      const { save } = useSave({ form, venue })
      return { form, save }
    },
    {
      initialProps: params,
      wrapper,
    }
  )
}

describe('useSave', () => {
  const logEvent = vi.fn()
  const snackBarSuccess = vi.fn()
  const snackBarError = vi.fn()
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
      logEvent,
    }))

    vi.spyOn(useSyncVenueCacheModule, 'useSyncVenueCache').mockReturnValue({
      syncVenue: vi.fn(),
      syncVenueWithData,
    })
  })

  it('should patch the venue, sync the cache, log success and show a success snackbar', async () => {
    const updatedVenue = { ...defaultGetVenue, bookingEmail: 'new@example.com' }
    vi.mocked(apiNew.editVenue).mockResolvedValueOnce(updatedVenue)

    const { result } = renderUseSave()

    await act(async () => {
      await result.current.save({ bookingEmail: 'new@example.com' })
    })

    expect(apiNew.editVenue).toHaveBeenCalledWith({
      path: { venue_id: Number(defaultGetVenue.id) },
      body: { bookingEmail: 'new@example.com' },
    })
    expect(syncVenueWithData).toHaveBeenCalledWith(
      defaultGetVenue.id,
      updatedVenue
    )
    expect(snackBarSuccess).toHaveBeenCalledWith(
      'Vos modifications ont été sauvegardées'
    )
    expect(logEvent).toHaveBeenCalledWith(Events.CLICKED_SAVE_VENUE, {
      saved: true,
      isEdition: true,
    })
  })

  it('should cast an empty bookingEmail to null before patching', async () => {
    vi.mocked(apiNew.editVenue).mockResolvedValueOnce(defaultGetVenue)

    const { result } = renderUseSave()

    await act(async () => {
      await result.current.save({ bookingEmail: '' })
    })

    expect(apiNew.editVenue).toHaveBeenCalledWith({
      path: { venue_id: Number(defaultGetVenue.id) },
      body: { bookingEmail: null },
    })
  })

  it('should set form errors when the API returns field-level errors', async () => {
    vi.mocked(apiNew.editVenue).mockRejectedValueOnce(
      new ApiError(
        {} as ApiRequestOptions,
        {
          status: 400,
          body: {
            bookingEmail: ['Adresse email invalide'],
          },
        } as ApiResult,
        ''
      )
    )

    const { result } = renderUseSave()
    const setError = vi.spyOn(result.current.form, 'setError')

    await act(async () => {
      await result.current.save({ bookingEmail: 'invalid@example.com' })
    })

    expect(setError).toHaveBeenCalledWith('bookingEmail', {
      type: 'bookingEmail',
      message: 'Adresse email invalide',
    })
    expect(snackBarError).toHaveBeenCalledWith(
      'Une ou plusieurs erreurs sont présentes dans le formulaire'
    )
    expect(syncVenueWithData).not.toHaveBeenCalled()
    expect(logEvent).toHaveBeenCalledWith(Events.CLICKED_SAVE_VENUE, {
      saved: false,
      isEdition: true,
    })
  })

  it('should show a generic error when the API returns a global error', async () => {
    vi.mocked(apiNew.editVenue).mockRejectedValueOnce(
      new ApiError(
        {} as ApiRequestOptions,
        {
          status: 500,
          body: { global: ['Boom'] },
        } as ApiResult,
        ''
      )
    )

    const { result } = renderUseSave()
    const setError = vi.spyOn(result.current.form, 'setError')

    await act(async () => {
      await result.current.save({ bookingEmail: 'new@example.com' })
    })

    expect(setError).not.toHaveBeenCalled()
    expect(snackBarError).toHaveBeenCalledWith(
      'Erreur lors de la sauvegarde de la structure.'
    )
    expect(logEvent).toHaveBeenCalledWith(Events.CLICKED_SAVE_VENUE, {
      saved: false,
      isEdition: true,
    })
  })

  it('should show a generic error when the thrown error is not an ApiError', async () => {
    vi.mocked(apiNew.editVenue).mockRejectedValueOnce(new Error('network down'))

    const { result } = renderUseSave()
    const setError = vi.spyOn(result.current.form, 'setError')

    await act(async () => {
      await result.current.save({ bookingEmail: 'new@example.com' })
    })

    expect(setError).not.toHaveBeenCalled()
    expect(snackBarError).toHaveBeenCalledWith(
      'Erreur lors de la sauvegarde de la structure.'
    )
    expect(logEvent).toHaveBeenCalledWith(Events.CLICKED_SAVE_VENUE, {
      saved: false,
      isEdition: true,
    })
  })
})
