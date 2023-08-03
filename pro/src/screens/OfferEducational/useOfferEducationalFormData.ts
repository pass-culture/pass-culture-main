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
  nationalPrograms: SelectOption[]
}

const useOfferEducationalFormData = (
  offererId: number | null,
  isNationalSystemActive: boolean,
  offer?: CollectiveOffer | CollectiveOfferTemplate
): OfferEducationalFormData & {
  isReady: boolean
  isNationalSystemActive: boolean
} => {
  const [isReady, setIsReady] = useState<boolean>(false)
  const defaultReturnValue: OfferEducationalFormData = {
    categories: { educationalCategories: [], educationalSubCategories: [] },
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
        isNationalSystemActive,
      })

      if (!result.isOk) {
        notify.error(result.message)
      }

      const { categories, offerers, domains, nationalPrograms } = result.payload

      setData({
        categories,
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
      loadData(offer)
    }
  }, [isReady, offer?.id, loadData, history])

  return {
    isReady,
    isNationalSystemActive,
    ...data,
  }
}

export default useOfferEducationalFormData
