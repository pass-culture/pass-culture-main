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
import { useNotification } from '@/commons/hooks/useNotification'
import { useOfferWizardMode } from '@/commons/hooks/useOfferWizardMode'
import { getIndividualOfferFactory } from '@/commons/utils/factories/individualApiFactories'
import { localStorageManager } from '@/commons/utils/localStorageManager'
import { LOCAL_STORAGE_USEFUL_INFORMATION_SUBMITTED } from '@/pages/IndividualOffer/IndividualOfferInformations/commons/constants'

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
vi.mock('@/commons/hooks/useNotification', () => ({
  useNotification: vi.fn(),
}))
vi.mock('@/commons/hooks/useOfferWizardMode', () => ({
  useOfferWizardMode: vi.fn(),
}))
vi.mock('@/commons/utils/localStorageManager', () => ({
  localStorageManager: { setItemIfNone: vi.fn() },
}))
vi.mock('@/commons/core/Offers/utils/getIndividualOfferUrl', () => ({
  getIndividualOfferUrl: vi.fn(),
}))
vi.mock('../../utils/toPatchOfferBodyModel', () => ({
  toPatchOfferBodyModel: vi.fn(),
}))

describe('useSaveOfferLocation', () => {
  const offer = getIndividualOfferFactory({ id: 123 })
  const setError = vi.fn() as unknown as UseFormSetError<LocationFormValues>

  let navigateMock: ReturnType<typeof useNavigate>
  let mutateMock: ReturnType<typeof vi.fn>
  let notificationMock: ReturnType<typeof useNotification>

  beforeEach(() => {
    vi.clearAllMocks()
    vi.mocked(api.patchOffer).mockResolvedValue(offer)
    vi.mocked(getIndividualOfferUrl).mockReturnValue('/mock-url')
    vi.mocked(useLocation).mockReturnValue({
      pathname: '/offers',
    } as unknown as ReturnType<typeof useLocation>)
    mutateMock = vi.fn().mockResolvedValue(undefined)
    vi.mocked(useSWRConfig).mockReturnValue({
      mutate: mutateMock,
    } as unknown as ReturnType<typeof useSWRConfig>)
    navigateMock = vi.fn() as unknown as ReturnType<typeof useNavigate>
    vi.mocked(useNavigate).mockReturnValue(navigateMock)
    notificationMock = { error: vi.fn() } as unknown as ReturnType<
      typeof useNotification
    >
    vi.mocked(useNotification).mockReturnValue(notificationMock)
    vi.mocked(useOfferWizardMode).mockReturnValue(OFFER_WIZARD_MODE.EDITION)
    vi.mocked(toPatchOfferBodyModel).mockReturnValue({})
  })

  it('saves and navigates to Useful Informations (read-only) in EDITION mode, updates cache, and sets local storage', async () => {
    const { saveAndContinue } = useSaveOfferLocation({ offer, setError })
    const formValues = makeLocationFormValues({ address: null })
    const requestBody: PatchOfferBodyModel = { shouldSendMail: true }
    vi.mocked(toPatchOfferBodyModel).mockReturnValueOnce(requestBody)
    await saveAndContinue({ formValues, shouldSendWarningMail: true })
    expect(toPatchOfferBodyModel).toHaveBeenCalledWith({
      offer,
      formValues,
      shouldSendWarningMail: true,
    })
    expect(api.patchOffer).toHaveBeenCalledWith(offer.id, requestBody)
    expect(mutateMock).toHaveBeenCalledWith([GET_OFFER_QUERY_KEY, offer.id])
    expect(localStorageManager.setItemIfNone).toHaveBeenCalledWith(
      `${LOCAL_STORAGE_USEFUL_INFORMATION_SUBMITTED}_${offer.id}`,
      'true'
    )
    expect(getIndividualOfferUrl).toHaveBeenCalledWith({
      offerId: offer.id,
      step: INDIVIDUAL_OFFER_WIZARD_STEP_IDS.USEFUL_INFORMATIONS,
      mode: OFFER_WIZARD_MODE.READ_ONLY,
      isOnboarding: false,
    })
    expect(navigateMock).toHaveBeenCalledWith('/mock-url')
    expect(notificationMock.error).not.toHaveBeenCalled()
    expect(setError).not.toHaveBeenCalled()
  })

  it('saves and navigates to Media in non-EDITION mode, no cache update, respects onboarding flag, default warningMail=false', async () => {
    vi.mocked(useOfferWizardMode).mockReturnValue(OFFER_WIZARD_MODE.CREATION)
    vi.mocked(useLocation).mockReturnValue({
      pathname: '/onboarding/create-offer',
    } as unknown as ReturnType<typeof useLocation>)
    const { saveAndContinue } = useSaveOfferLocation({ offer, setError })
    const formValues = makeLocationFormValues({ address: null })
    await saveAndContinue({ formValues })
    expect(toPatchOfferBodyModel).toHaveBeenCalledWith({
      offer,
      formValues,
      shouldSendWarningMail: false,
    })
    expect(api.patchOffer).toHaveBeenCalled()
    expect(mutateMock).not.toHaveBeenCalled()
    expect(getIndividualOfferUrl).toHaveBeenCalledWith({
      offerId: offer.id,
      step: INDIVIDUAL_OFFER_WIZARD_STEP_IDS.MEDIA,
      mode: OFFER_WIZARD_MODE.CREATION,
      isOnboarding: true,
    })
    expect(localStorageManager.setItemIfNone).toHaveBeenCalledWith(
      `${LOCAL_STORAGE_USEFUL_INFORMATION_SUBMITTED}_${offer.id}`,
      'true'
    )
    expect(navigateMock).toHaveBeenCalledWith('/mock-url')
    expect(notificationMock.error).not.toHaveBeenCalled()
    expect(setError).not.toHaveBeenCalled()
  })

  it('returns early when serialization throws (no API call or side-effects)', async () => {
    const { saveAndContinue } = useSaveOfferLocation({ offer, setError })
    const formValues = makeLocationFormValues({ address: null })
    vi.mocked(toPatchOfferBodyModel).mockImplementationOnce(() => {
      throw new Error('serialize')
    })
    await saveAndContinue({ formValues })
    expect(api.patchOffer).not.toHaveBeenCalled()
    expect(mutateMock).not.toHaveBeenCalled()
    expect(localStorageManager.setItemIfNone).not.toHaveBeenCalled()
    expect(getIndividualOfferUrl).not.toHaveBeenCalled()
    expect(navigateMock).not.toHaveBeenCalled()
    expect(notificationMock.error).not.toHaveBeenCalled()
    expect(setError).not.toHaveBeenCalled()
  })

  it('handles API error by setting field errors and notifying the user', async () => {
    const apiError = {
      body: {
        addressAutocomplete: 'Invalid address',
        postalCode: 'Invalid postal code',
      },
    }
    vi.mocked(api.patchOffer).mockRejectedValueOnce(apiError)
    vi.mocked(isErrorAPIError).mockReturnValue(true)
    const { saveAndContinue } = useSaveOfferLocation({ offer, setError })
    await saveAndContinue({
      formValues: makeLocationFormValues({ address: null }),
    })
    expect(setError).toHaveBeenCalledWith('addressAutocomplete', {
      message: 'Invalid address',
    })
    expect(setError).toHaveBeenCalledWith('postalCode', {
      message: 'Invalid postal code',
    })
    expect(notificationMock.error).toHaveBeenCalledWith(SENT_DATA_ERROR_MESSAGE)
    expect(navigateMock).not.toHaveBeenCalled()
    expect(mutateMock).not.toHaveBeenCalled()
  })

  it('silently returns on non-API errors (no notifications or field errors)', async () => {
    vi.mocked(api.patchOffer).mockRejectedValueOnce(new Error('network'))
    vi.mocked(isErrorAPIError).mockReturnValue(false)
    const { saveAndContinue } = useSaveOfferLocation({ offer, setError })
    await saveAndContinue({
      formValues: makeLocationFormValues({ address: null }),
    })
    expect(setError).not.toHaveBeenCalled()
    expect(notificationMock.error).not.toHaveBeenCalled()
    expect(navigateMock).not.toHaveBeenCalled()
    expect(mutateMock).not.toHaveBeenCalled()
  })
})
