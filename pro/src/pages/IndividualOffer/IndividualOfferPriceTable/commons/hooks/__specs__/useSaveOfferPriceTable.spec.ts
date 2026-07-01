import { act, renderHook } from '@testing-library/react'
import { useForm } from 'react-hook-form'
import * as reactRouter from 'react-router'

import {
  ApiError,
  type ApiRequestOptions,
  type ApiResult,
} from '@/apiClient/compat'
import { OFFER_WIZARD_MODE } from '@/commons/core/Offers/constants'
import { useActiveFeature } from '@/commons/hooks/useActiveFeature'
import { useOfferWizardMode } from '@/commons/hooks/useOfferWizardMode'
import * as useSnackBar from '@/commons/hooks/useSnackBar'
import { getIndividualOfferFactory } from '@/commons/utils/factories/individualApiFactories'

import type { PriceTableFormValues } from '../../schemas'
import { saveEventOfferPriceTable } from '../../utils/saveEventOfferPriceTable'
import { saveNonEventOfferPriceTable } from '../../utils/saveNonEventOfferPriceTable'
import { useSaveOfferPriceTable } from '../useSaveOfferPriceTable'

vi.mock('react-router', async () => {
  const actual =
    await vi.importActual<typeof import('react-router')>('react-router')
  return {
    ...actual,
    useNavigate: vi.fn(),
    useLocation: vi.fn(),
  }
})
vi.mock('@/commons/hooks/useOfferWizardMode', () => ({
  useOfferWizardMode: vi.fn(),
}))
vi.mock('../../utils/saveEventOfferPriceTable', () => ({
  saveEventOfferPriceTable: vi.fn(() => Promise.resolve()),
}))
vi.mock('../../utils/saveNonEventOfferPriceTable', () => ({
  saveNonEventOfferPriceTable: vi.fn(() => Promise.resolve()),
}))
vi.mock('@/commons/hooks/useActiveFeature', () => ({
  useActiveFeature: vi.fn(),
}))
vi.mock('@/commons/hooks/useSyncVenueCache', () => ({
  useSyncVenueCache: () => ({
    syncVenue: vi.fn(),
    syncVenueWithData: vi.fn(),
  }),
}))

const renderUseSaveOfferPriceTable = (params: {
  offer: ReturnType<typeof getIndividualOfferFactory>
}) => {
  const defaultValues = {
    priceCategories: [
      {
        activationCodes: [],
        activationCodesExpirationDatetime: '',
        bookingLimitDatetime: '',
        bookingsQuantity: undefined,
        id: undefined,
        label: 'Tarif unique',
        price: 10,
        quantity: 5,
        offerId: 1,
        remainingQuantity: null,
      },
    ],
    isDuo: true,
  }

  return renderHook(
    ({ offer }) => {
      const form = useForm<PriceTableFormValues>({
        defaultValues,
      })
      const save = useSaveOfferPriceTable({ form, offer })
      return { form, ...save }
    },
    { initialProps: params }
  )
}

describe('useSaveOfferPriceTable', () => {
  const useLocationMockReturnValue: reactRouter.Location = {
    hash: '',
    key: '',
    pathname: '/offers',
    search: '',
    state: {},
  }

  const snackBarError = vi.fn()
  const snackBarSuccess = vi.fn()

  beforeEach(async () => {
    const snackBarsImport = (await vi.importActual(
      '@/commons/hooks/useSnackBar'
    )) as ReturnType<typeof useSnackBar.useSnackBar>
    vi.spyOn(useSnackBar, 'useSnackBar').mockImplementation(() => ({
      ...snackBarsImport,
      success: snackBarSuccess,
      error: snackBarError,
    }))

    vi.mocked(useActiveFeature).mockReturnValueOnce(true)
  })

  it('should not save but return success when EDITION mode and form not dirty', async () => {
    vi.mocked(useOfferWizardMode).mockReturnValue(OFFER_WIZARD_MODE.EDITION)
    vi.mocked(reactRouter.useLocation).mockReturnValue(
      useLocationMockReturnValue
    )

    const offer = getIndividualOfferFactory({ id: 99, isEvent: false })

    const { result } = renderUseSaveOfferPriceTable({ offer })

    let hasSucceeded: boolean | undefined
    await act(async () => {
      hasSucceeded = await result.current.save(result.current.form.getValues())
    })

    expect(hasSucceeded).toBe(true)
    expect(saveNonEventOfferPriceTable).not.toHaveBeenCalled()
    expect(saveEventOfferPriceTable).not.toHaveBeenCalled()
    expect(snackBarSuccess).toHaveBeenCalled()
  })

  it('should save non-event offer (creation) and return success', async () => {
    vi.mocked(useOfferWizardMode).mockReturnValue(OFFER_WIZARD_MODE.CREATION)
    vi.spyOn(reactRouter, 'useLocation').mockReturnValue(
      useLocationMockReturnValue
    )

    const offer = getIndividualOfferFactory({ id: 42, isEvent: false })

    const { result } = renderUseSaveOfferPriceTable({ offer })

    act(() => {
      result.current.form.setValue('priceCategories.0.price', 15)
      result.current.form.formState = {
        ...result.current.form.formState,
        isDirty: true,
      }
    })
    let hasSucceeded: boolean | undefined
    await act(async () => {
      hasSucceeded = await result.current.save(result.current.form.getValues())
    })

    expect(hasSucceeded).toBe(true)
    expect(saveNonEventOfferPriceTable).toHaveBeenCalled()
  })

  it('should save event offer (creation) and return success', async () => {
    vi.mocked(useOfferWizardMode).mockReturnValue(OFFER_WIZARD_MODE.CREATION)
    vi.spyOn(reactRouter, 'useLocation').mockReturnValue(
      useLocationMockReturnValue
    )

    const offer = getIndividualOfferFactory({ id: 5, isEvent: true })

    const { result } = renderUseSaveOfferPriceTable({ offer })

    act(() => {
      result.current.form.setValue('priceCategories.0.price', 20)
      result.current.form.formState = {
        ...result.current.form.formState,
        isDirty: true,
      }
    })
    let hasSucceeded: boolean | undefined
    await act(async () => {
      hasSucceeded = await result.current.save(result.current.form.getValues())
    })

    expect(hasSucceeded).toBe(true)
    expect(saveEventOfferPriceTable).toHaveBeenCalled()
  })

  it('should notify error and return false when save functions throw', async () => {
    vi.mocked(useOfferWizardMode).mockReturnValue(OFFER_WIZARD_MODE.CREATION)
    vi.spyOn(reactRouter, 'useLocation').mockReturnValue(
      useLocationMockReturnValue
    )
    vi.mocked(saveNonEventOfferPriceTable).mockRejectedValueOnce(
      new Error('boom')
    )

    const offer = getIndividualOfferFactory({ id: 7, isEvent: false })

    const { result } = renderUseSaveOfferPriceTable({ offer })
    act(() => {
      result.current.form.setValue('priceCategories.0.price', 22)
      result.current.form.formState = {
        ...result.current.form.formState,
        isDirty: true,
      }
    })
    let hasSucceeded: boolean | undefined
    await act(async () => {
      hasSucceeded = await result.current.save(result.current.form.getValues())
    })

    expect(hasSucceeded).toBe(false)
    expect(snackBarError).toHaveBeenCalledWith(
      'Une erreur est survenue lors de la mise à jour de votre offre'
    )
  })

  it('should set the form with api error and return false', async () => {
    vi.mocked(useOfferWizardMode).mockReturnValue(OFFER_WIZARD_MODE.CREATION)
    vi.spyOn(reactRouter, 'useLocation').mockReturnValue(
      useLocationMockReturnValue
    )

    vi.mocked(saveNonEventOfferPriceTable).mockRejectedValueOnce(
      new ApiError(
        {} as ApiRequestOptions,
        {
          status: 400,
          body: {
            'priceCategories.0.bookingLimitDatetime': [
              'API bookingLimitDatetime ERROR',
            ],
          },
        } as ApiResult,
        ''
      )
    )

    const offer = getIndividualOfferFactory({ id: 7, isEvent: false })

    const { result } = renderUseSaveOfferPriceTable({ offer })

    const spyFormSetError = vi.spyOn(result.current.form, 'setError')

    let hasSucceeded: boolean | undefined
    await act(async () => {
      result.current.form.formState = {
        ...result.current.form.formState,
        isDirty: true,
      }
      hasSucceeded = await result.current.save(result.current.form.getValues())
    })

    expect(hasSucceeded).toBe(false)
    expect(spyFormSetError).toHaveBeenCalledWith(
      'priceCategories.0.bookingLimitDatetime',
      {
        type: 'custom',
        message: 'API bookingLimitDatetime ERROR',
      }
    )
  })
})
