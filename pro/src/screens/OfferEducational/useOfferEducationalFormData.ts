import { useState, useCallback, useEffect } from 'react'

import { GetEducationalOffererResponseModel } from 'apiClient/v1'
import {
  CollectiveOffer,
  CollectiveOfferTemplate,
  EducationalCategories,
} from 'core/OfferEducational'
import getCollectiveOfferFormDataApdater from 'core/OfferEducational/adapters/getCollectiveOfferFormDataAdapter'
import { SelectOption } from 'custom_types/form'
import useNotification from 'hooks/useNotification'

type OfferEducationalFormData = {
  categories: EducationalCategories
  domains: SelectOption[]
  offerers: GetEducationalOffererResponseModel[]
}

const useOfferEducationalFormData = (
  offererId: number | null,
  offer?: CollectiveOffer | CollectiveOfferTemplate
): OfferEducationalFormData & { isReady: boolean } => {
  const [isReady, setIsReady] = useState<boolean>(false)
  const defaultReturnValue: OfferEducationalFormData = {
    categories: { educationalCategories: [], educationalSubCategories: [] },
    domains: [],
    offerers: [],
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

      const { categories, offerers, domains } = result.payload

      setData({
        categories,
        offerers,
        domains,
      })

      setIsReady(true)
    },
    [notify]
  )

  useEffect(() => {
    if (!isReady) {
      loadData(offer)
    }
  }, [isReady, offer?.id, loadData, history])

  return {
    isReady,
    ...data,
  }
}

export default useOfferEducationalFormData
