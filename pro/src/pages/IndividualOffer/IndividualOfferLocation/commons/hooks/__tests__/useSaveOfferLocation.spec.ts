import type { UseFormSetError } from 'react-hook-form'
import { useLocation, useNavigate } from 'react-router'
import { useSWRConfig } from 'swr'

import { api } from '@/apiClient/api'
import { isErrorAPIError } from '@/apiClient/helpers'
import type { PatchOfferBodyModel } from '@/apiClient/v1'
import { GET_OFFER_QUERY_KEY } from '@/commons/config/swrQueryKeys'
import { OFFER_WIZARD_MODE } from '@/commons/core/Offers/constants'
import { getIndividualOfferUrl } from '@/commons/core/Offers/utils/getIndividualOfferUrl'
import { SENT_DATA_ERROR_MESSAGE } from '@/commons/core/shared/constants'
import { useActiveFeature } from '@/commons/hooks/useActiveFeature'
import { useOfferWizardMode } from '@/commons/hooks/useOfferWizardMode'
import { useSnackBar } from '@/commons/hooks/useSnackBar'
import { getIndividualOfferFactory } from '@/commons/utils/factories/individualApiFactories'

import { makeLocationFormValues } from '../../__mocks__/makeLocationFormValues'
import type { LocationFormValues } from '../../types'
import { toPatchOfferBodyModel } from '../../utils/toPatchOfferBodyModel'
import { useSaveOfferLocation } from '../useSaveOfferLocation'

vi.mock('react-router', () => ({
  useLocation: vi.fn(),
  useNavigate: vi.fn(),
}))
vi.mock('swr', () => ({
  useSWRConfig: vi.fn(),
}))
vi.mock('@/apiClient/api', () => ({
  api: { patchOffer: vi.fn() },
}))
vi.mock('@/apiClient/helpers', () => ({
  isErrorAPIError: vi.fn(),
}))
vi.mock('@/commons/hooks/useSnackBar', () => ({
  useSnackBar: vi.fn(),
}))
vi.mock('@/commons/hooks/useOfferWizardMode', () => ({
  useOfferWizardMode: vi.fn(),
}))
vi.mock('@/commons/hooks/useActiveFeature', () => ({
  useActiveFeature: vi.fn(),
}))
vi.mock('@/commons/core/Offers/utils/getIndividualOfferUrl', () => ({
  getIndividualOfferUrl: vi.fn(),
}))
vi.mock('../../utils/toPatchOfferBodyModel', () => ({
  toPatchOfferBodyModel: vi.fn(),
}))

describe('useSaveOfferLocation', () => {
  const offerBase = getIndividualOfferFactory({ id: 123 })
  const setErrorMock = vi.fn() as unknown as UseFormSetError<LocationFormValues>

  let navigateMock: ReturnType<typeof useNavigate>
  let mutateMock: ReturnType<typeof vi.fn>
  let notificationMock: ReturnType<typeof useSnackBar>

  beforeEach(() => {
    vi.mocked(api.patchOffer).mockResolvedValue(offerBase)
    vi.mocked(getIndividualOfferUrl).mockReturnValue('/mock-url')
    vi.mocked(useLocation).mockReturnValue({
      pathname: '/offers',
    } as unknown as ReturnType<typeof useLocation>)
    mutateMock = vi.fn((_key, promise) => promise)
    vi.mocked(useSWRConfig).mockReturnValue({
      mutate: mutateMock,
    } as unknown as ReturnType<typeof useSWRConfig>)
    navigateMock = vi.fn()
    vi.mocked(useNavigate).mockReturnValue(navigateMock)
    notificationMock = {
      error: vi.fn(),
      success: vi.fn(),
    } as unknown as ReturnType<typeof useSnackBar>
    vi.mocked(useSnackBar).mockReturnValue(notificationMock)
    vi.mocked(useOfferWizardMode).mockReturnValue(OFFER_WIZARD_MODE.EDITION)
    vi.mocked(useActiveFeature).mockReturnValue(false)
    vi.mocked(toPatchOfferBodyModel).mockReturnValue({})
  })

  it('should save and update the cache in EDITION mode, forwarding shouldSendMail', async () => {
    const requestBody: PatchOfferBodyModel = { shouldSendMail: true }
    vi.mocked(toPatchOfferBodyModel).mockReturnValueOnce(requestBody)

    const formValues = makeLocationFormValues({ location: null })

    const { save } = useSaveOfferLocation({
      offer: offerBase,
      setError: setErrorMock,
    })
    const hasSucceeded = await save({
      formValues,
      shouldSendMail: true,
    })

    expect(hasSucceeded).toBe(true)
    expect(toPatchOfferBodyModel).toHaveBeenCalledWith({
      offer: offerBase,
      formValues,
      shouldSendMail: true,
    })
    expect(api.patchOffer).toHaveBeenCalledWith({
      path: { offer_id: offerBase.id },
      body: requestBody,
    })
    expect(mutateMock).toHaveBeenCalledWith(
      [GET_OFFER_QUERY_KEY, offerBase.id],
      expect.anything(),
      { revalidate: false }
    )
    expect(notificationMock.error).not.toHaveBeenCalled()
    expect(setErrorMock).not.toHaveBeenCalled()
  })

  it('should save and update the cache in non-EDITION mode, defaulting shouldSendMail to false', async () => {
    vi.mocked(useOfferWizardMode).mockReturnValue(OFFER_WIZARD_MODE.CREATION)
    vi.mocked(useLocation).mockReturnValue({
      pathname: '/onboarding/create-offer',
    } as unknown as ReturnType<typeof useLocation>)

    const formValues = makeLocationFormValues({ location: null })

    const { save } = useSaveOfferLocation({
      offer: offerBase,
      setError: setErrorMock,
    })
    const hasSucceeded = await save({ formValues })

    expect(hasSucceeded).toBe(true)
    expect(toPatchOfferBodyModel).toHaveBeenCalledWith({
      offer: offerBase,
      formValues,
      shouldSendMail: false,
    })
    expect(api.patchOffer).toHaveBeenCalled()
    expect(mutateMock).toHaveBeenCalledWith(
      [GET_OFFER_QUERY_KEY, offerBase.id],
      expect.anything(),
      { revalidate: false }
    )
    expect(notificationMock.error).not.toHaveBeenCalled()
    expect(setErrorMock).not.toHaveBeenCalled()
  })

  it('should return early when serialization throws (no API call or side-effects)', async () => {
    vi.mocked(toPatchOfferBodyModel).mockImplementationOnce(() => {
      throw new Error('serialize')
    })

    const formValues = makeLocationFormValues({ location: null })

    const { save } = useSaveOfferLocation({
      offer: offerBase,
      setError: setErrorMock,
    })
    await save({ formValues })

    expect(api.patchOffer).not.toHaveBeenCalled()
    expect(mutateMock).not.toHaveBeenCalled()
    expect(getIndividualOfferUrl).not.toHaveBeenCalled()
    expect(navigateMock).not.toHaveBeenCalled()
    expect(notificationMock.error).not.toHaveBeenCalled()
    expect(setErrorMock).not.toHaveBeenCalled()
  })

  it('should handle API error by setting field errors and notifying the user', async () => {
    const apiError = {
      body: {
        addressAutocomplete: 'Invalid address',
        postalCode: 'Invalid postal code',
      },
    }
    vi.mocked(api.patchOffer).mockRejectedValueOnce(apiError)
    vi.mocked(isErrorAPIError).mockReturnValue(true)

    const { save } = useSaveOfferLocation({
      offer: offerBase,
      setError: setErrorMock,
    })
    await save({
      formValues: makeLocationFormValues({ location: null }),
    })

    expect(setErrorMock).toHaveBeenCalledWith('addressAutocomplete', {
      message: 'Invalid address',
    })
    expect(setErrorMock).toHaveBeenCalledWith('postalCode', {
      message: 'Invalid postal code',
    })
    expect(notificationMock.error).toHaveBeenCalledWith(SENT_DATA_ERROR_MESSAGE)
    expect(navigateMock).not.toHaveBeenCalled()
  })

  it('should show success snackbar without navigating in EDITION mode when WIP_OFFER_EXPOSURE is enabled', async () => {
    vi.mocked(useActiveFeature).mockReturnValue(true)
    const formValues = makeLocationFormValues({ location: null })

    const { save } = useSaveOfferLocation({
      offer: offerBase,
      setError: setErrorMock,
    })
    await save({ formValues })

    expect(notificationMock.success).toHaveBeenCalledWith(
      'Votre offre a bien été modifiée.'
    )
    expect(getIndividualOfferUrl).not.toHaveBeenCalled()
    expect(navigateMock).not.toHaveBeenCalled()
  })

  it('should silently return on non-API errors (no notifications or field errors)', async () => {
    vi.mocked(api.patchOffer).mockRejectedValueOnce(new Error('network'))
    vi.mocked(isErrorAPIError).mockReturnValue(false)

    const { save } = useSaveOfferLocation({
      offer: offerBase,
      setError: setErrorMock,
    })
    await save({
      formValues: makeLocationFormValues({ location: null }),
    })

    expect(setErrorMock).not.toHaveBeenCalled()
    expect(notificationMock.error).not.toHaveBeenCalled()
    expect(navigateMock).not.toHaveBeenCalled()
  })
})
