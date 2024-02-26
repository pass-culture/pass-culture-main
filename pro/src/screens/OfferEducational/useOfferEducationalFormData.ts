import { useState, useCallback, useEffect } from 'react'

import { GetEducationalOffererResponseModel } from 'apiClient/v1'
import { CollectiveOffer, CollectiveOfferTemplate } from 'core/OfferEducational'
import getCollectiveOfferFormDataApdater from 'core/OfferEducational/adapters/getCollectiveOfferFormDataAdapter'
import { SelectOption } from 'custom_types/form'
import useNotification from 'hooks/useNotification'

type OfferEducationalFormData = {
  domains: SelectOption[]
  offerers: GetEducationalOffererResponseModel[]
  nationalPrograms: SelectOption<number>[]
}

const useOfferEducationalFormData = (
  offererId: number | null,
  offer?: CollectiveOffer | CollectiveOfferTemplate
): OfferEducationalFormData & {
  isReady: boolean
} => {
  const [isReady, setIsReady] = useState<boolean>(false)
  const defaultReturnValue: OfferEducationalFormData = {
    domains: [],
    offerers: [],
    nationalPrograms: [],
  }
  const [data, setData] = useState<OfferEducationalFormData>(defaultReturnValue)
  const notify = useNotification()

  const loadData = useCallback(
    async (offerResponse?: CollectiveOffer | CollectiveOfferTemplate) => {
      const result = await getCollectiveOfferFormDataApdater({
        offererId,
        offer: offerResponse,
      })

      if (!result.isOk) {
        notify.error(result.message)
      }

      const { offerers, domains, nationalPrograms } = result.payload

      setData({
        offerers,
        domains,
        nationalPrograms,
      })

      setIsReady(true)
    },
    [notify]
  )

  useEffect(() => {
    if (!isReady) {
      // eslint-disable-next-line @typescript-eslint/no-floating-promises
      loadData(offer)
    }
  }, [isReady, offer?.id, loadData, history])

  return {
    isReady,
    ...data,
  }
}

export default useOfferEducationalFormData
