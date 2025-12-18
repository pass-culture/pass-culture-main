import type { UseFormSetError } from 'react-hook-form'
import { useLocation, useNavigate } from 'react-router'
import { useSWRConfig } from 'swr'

import { api } from '@/apiClient/api'
import { isErrorAPIError } from '@/apiClient/helpers'
import type { PatchOfferBodyModel } from '@/apiClient/v1'
import { GET_OFFER_QUERY_KEY } from '@/commons/config/swrQueryKeys'
import {
  INDIVIDUAL_OFFER_WIZARD_STEP_IDS,
  OFFER_WIZARD_MODE,
} from '@/commons/core/Offers/constants'
import { getIndividualOfferUrl } from '@/commons/core/Offers/utils/getIndividualOfferUrl'
import { SENT_DATA_ERROR_MESSAGE } from '@/commons/core/shared/constants'
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
    vi.clearAllMocks()
    vi.mocked(api.patchOffer).mockResolvedValue(offerBase)
    vi.mocked(getIndividualOfferUrl).mockReturnValue('/mock-url')
    vi.mocked(useLocation).mockReturnValue({
      pathname: '/offers',
    } as unknown as ReturnType<typeof useLocation>)
    mutateMock = vi.fn((_key, promise) => promise)
    vi.mocked(useSWRConfig).mockReturnValue({
      mutate: mutateMock,
    } as unknown as ReturnType<typeof useSWRConfig>)
    navigateMock = vi.fn() as unknown as ReturnType<typeof useNavigate>
    vi.mocked(useNavigate).mockReturnValue(navigateMock)
    notificationMock = { error: vi.fn() } as unknown as ReturnType<
      typeof useSnackBar
    >
    vi.mocked(useSnackBar).mockReturnValue(notificationMock)
    vi.mocked(useOfferWizardMode).mockReturnValue(OFFER_WIZARD_MODE.EDITION)
    vi.mocked(toPatchOfferBodyModel).mockReturnValue({})
  })

  it('should save and navigate to Useful Informations (read-only) in EDITION mode, update cache, and set local storage', async () => {
    const requestBody: PatchOfferBodyModel = { shouldSendMail: true }
    vi.mocked(toPatchOfferBodyModel).mockReturnValueOnce(requestBody)

    const formValues = makeLocationFormValues({ location: null })

    const { saveAndContinue } = useSaveOfferLocation({
      offer: offerBase,
      setError: setErrorMock,
    })
    await saveAndContinue({
      formValues,
      shouldSendMail: true,
    })

    expect(toPatchOfferBodyModel).toHaveBeenCalledWith({
      offer: offerBase,
      formValues,
      shouldSendMail: true,
    })
    expect(api.patchOffer).toHaveBeenCalledWith(offerBase.id, requestBody)
    expect(mutateMock).toHaveBeenCalledWith(
      [GET_OFFER_QUERY_KEY, offerBase.id],
      expect.anything(),
      { revalidate: false }
    )
    expect(getIndividualOfferUrl).toHaveBeenCalledWith({
      offerId: offerBase.id,
      step: INDIVIDUAL_OFFER_WIZARD_STEP_IDS.LOCATION,
      mode: OFFER_WIZARD_MODE.READ_ONLY,
      isOnboarding: false,
    })
    expect(navigateMock).toHaveBeenCalledWith('/mock-url')
    expect(notificationMock.error).not.toHaveBeenCalled()
    expect(setErrorMock).not.toHaveBeenCalled()
  })

  it('should save and navigate to Media in non-EDITION mode, no cache update, respect onboarding flag, default warningMail=false', async () => {
    vi.mocked(useOfferWizardMode).mockReturnValue(OFFER_WIZARD_MODE.CREATION)
    vi.mocked(useLocation).mockReturnValue({
      pathname: '/onboarding/create-offer',
    } as unknown as ReturnType<typeof useLocation>)

    const formValues = makeLocationFormValues({ location: null })

    const { saveAndContinue } = useSaveOfferLocation({
      offer: offerBase,
      setError: setErrorMock,
    })
    await saveAndContinue({ formValues })

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
    expect(getIndividualOfferUrl).toHaveBeenCalledWith({
      offerId: offerBase.id,
      step: INDIVIDUAL_OFFER_WIZARD_STEP_IDS.MEDIA,
      mode: OFFER_WIZARD_MODE.CREATION,
      isOnboarding: true,
    })
    expect(navigateMock).toHaveBeenCalledWith('/mock-url')
    expect(notificationMock.error).not.toHaveBeenCalled()
    expect(setErrorMock).not.toHaveBeenCalled()
  })

  it('should return early when serialization throws (no API call or side-effects)', async () => {
    vi.mocked(toPatchOfferBodyModel).mockImplementationOnce(() => {
      throw new Error('serialize')
    })

    const formValues = makeLocationFormValues({ location: null })

    const { saveAndContinue } = useSaveOfferLocation({
      offer: offerBase,
      setError: setErrorMock,
    })
    await saveAndContinue({ formValues })

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

    const { saveAndContinue } = useSaveOfferLocation({
      offer: offerBase,
      setError: setErrorMock,
    })
    await saveAndContinue({
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

  it('should silently return on non-API errors (no notifications or field errors)', async () => {
    vi.mocked(api.patchOffer).mockRejectedValueOnce(new Error('network'))
    vi.mocked(isErrorAPIError).mockReturnValue(false)

    const { saveAndContinue } = useSaveOfferLocation({
      offer: offerBase,
      setError: setErrorMock,
    })
    await saveAndContinue({
      formValues: makeLocationFormValues({ location: null }),
    })

    expect(setErrorMock).not.toHaveBeenCalled()
    expect(notificationMock.error).not.toHaveBeenCalled()
    expect(navigateMock).not.toHaveBeenCalled()
  })
})
