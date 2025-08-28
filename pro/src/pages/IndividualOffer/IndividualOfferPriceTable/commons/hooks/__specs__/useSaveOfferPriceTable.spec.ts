import { act, renderHook } from '@testing-library/react'
import { useForm } from 'react-hook-form'
import * as reactRouter from 'react-router'

import { OFFER_WIZARD_MODE } from '@/commons/core/Offers/constants'
import { useNotification } from '@/commons/hooks/useNotification'
import { useOfferWizardMode } from '@/commons/hooks/useOfferWizardMode'
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
vi.mock('@/commons/hooks/useNotification', () => ({
  useNotification: vi.fn(),
}))
vi.mock('@/commons/hooks/useOfferWizardMode', () => ({
  useOfferWizardMode: vi.fn(),
}))
vi.mock('../../utils/saveEventOfferPriceTable', () => ({
  saveEventOfferPriceTable: vi.fn(() => Promise.resolve()),
}))
vi.mock('../../utils/saveNonEventOfferPriceTable', () => ({
  saveNonEventOfferPriceTable: vi.fn(() => Promise.resolve()),
}))
vi.mock('@/components/IndividualOffer/utils/getSuccessMessage', () => ({
  getSuccessMessage: () => 'ok',
}))

const renderUseSaveOfferPriceTable = (params: {
  offer: ReturnType<typeof getIndividualOfferFactory>
}) => {
  const defaultValues = {
    entries: [
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
  const useNotificationMockReturnValue: ReturnType<typeof useNotification> = {
    success: vi.fn(),
    error: vi.fn(),
    information: vi.fn(),
    close: () => ({
      payload: undefined,
      type: 'notifications/closeNotification',
    }),
  }

  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('should early navigate + success when EDITION mode and form not dirty', async () => {
    vi.mocked(useOfferWizardMode).mockReturnValue(OFFER_WIZARD_MODE.EDITION)
    vi.mocked(reactRouter.useLocation).mockReturnValue(
      useLocationMockReturnValue
    )
    const useNavigateMock = vi.fn()
    vi.spyOn(reactRouter, 'useNavigate').mockReturnValue(useNavigateMock)
    vi.mocked(useNotification).mockReturnValue(useNotificationMockReturnValue)

    const offer = getIndividualOfferFactory({ id: 99, isEvent: false })

    const { result } = renderUseSaveOfferPriceTable({ offer })
    await act(async () => {
      await result.current.saveAndContinue(result.current.form.getValues())
    })

    expect(saveNonEventOfferPriceTable).not.toHaveBeenCalled()
    expect(saveEventOfferPriceTable).not.toHaveBeenCalled()
    // SWR mutate not asserted (real SWR not mocked)
    expect(useNavigateMock).toHaveBeenCalledWith(
      expect.stringMatching(`/offre/individuelle/${offer.id}/tarifs$`)
    )
    expect(useNotification().success).toHaveBeenCalled()
  })

  it('should save non-event offer (creation) and navigate to summary', async () => {
    vi.mocked(useOfferWizardMode).mockReturnValue(OFFER_WIZARD_MODE.CREATION)
    vi.spyOn(reactRouter, 'useLocation').mockReturnValue(
      useLocationMockReturnValue
    )
    const useNavigateMock = vi.fn()
    vi.spyOn(reactRouter, 'useNavigate').mockReturnValue(useNavigateMock)

    const offer = getIndividualOfferFactory({ id: 42, isEvent: false })

    const { result } = renderUseSaveOfferPriceTable({ offer })

    act(() => {
      result.current.form.setValue('entries.0.price', 15)
    })
    await act(async () => {
      await result.current.saveAndContinue(result.current.form.getValues())
    })

    expect(saveNonEventOfferPriceTable).toHaveBeenCalled()
    expect(useNavigateMock).toHaveBeenCalledWith(
      expect.stringMatching(
        `/offre/individuelle/${offer.id}/creation/recapitulatif$`
      )
    )
  })

  it('should save event offer (creation) and navigate to stocks step', async () => {
    vi.mocked(useOfferWizardMode).mockReturnValue(OFFER_WIZARD_MODE.CREATION)
    vi.spyOn(reactRouter, 'useLocation').mockReturnValue(
      useLocationMockReturnValue
    )
    const useNavigateMock = vi.fn()
    vi.spyOn(reactRouter, 'useNavigate').mockReturnValue(useNavigateMock)

    const offer = getIndividualOfferFactory({ id: 5, isEvent: true })

    const { result } = renderUseSaveOfferPriceTable({ offer })

    act(() => {
      result.current.form.setValue('entries.0.price', 20)
    })
    await act(async () => {
      await result.current.saveAndContinue(result.current.form.getValues())
    })

    expect(saveEventOfferPriceTable).toHaveBeenCalled()
    expect(useNavigateMock).toHaveBeenCalledWith(
      '/offre/individuelle/5/creation/stocks'
    )
  })

  it('should notify error when save functions throw', async () => {
    vi.mocked(useOfferWizardMode).mockReturnValue(OFFER_WIZARD_MODE.CREATION)
    vi.spyOn(reactRouter, 'useLocation').mockReturnValue(
      useLocationMockReturnValue
    )
    const useNavigateMock = vi.fn()
    vi.spyOn(reactRouter, 'useNavigate').mockReturnValue(useNavigateMock)
    vi.mocked(useNotification).mockReturnValue(useNotificationMockReturnValue)
    vi.mocked(saveNonEventOfferPriceTable).mockRejectedValueOnce(
      new Error('boom')
    )

    const offer = getIndividualOfferFactory({ id: 7, isEvent: false })

    const { result } = renderUseSaveOfferPriceTable({ offer })
    act(() => {
      result.current.form.setValue('entries.0.price', 22)
    })
    await act(async () => {
      await result.current.saveAndContinue(result.current.form.getValues())
    })

    expect(useNotification().error).toHaveBeenCalledWith('boom')
    expect(useNavigateMock).not.toHaveBeenCalled()
  })
})
