import { useCallback, useEffect, useState } from 'react'

import { api } from 'apiClient/api'
import {
  GetCollectiveOfferResponseModel,
  GetCollectiveOfferTemplateResponseModel,
  GetEducationalOffererResponseModel,
} from 'apiClient/v1'
import { getUserOfferersFromOffer } from 'core/OfferEducational/utils/getUserOfferersFromOffer'
import { serializeEducationalOfferers } from 'core/OfferEducational/utils/serializeEducationalOfferers'
import { GET_DATA_ERROR_MESSAGE } from 'core/shared/constants'
import { SelectOption } from 'custom_types/form'
import { useNotification } from 'hooks/useNotification'

type OfferEducationalFormData = {
  domains: SelectOption[]
  offerers: GetEducationalOffererResponseModel[]
  nationalPrograms: SelectOption<number>[]
}

// TODO: Delete this hook and use useSwr where needed.
export const useOfferEducationalFormData = (
  offererId: number | null,
  offer?:
    | GetCollectiveOfferResponseModel
    | GetCollectiveOfferTemplateResponseModel
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
    async (
      offerResponse?:
        | GetCollectiveOfferResponseModel
        | GetCollectiveOfferTemplateResponseModel
    ) => {
      try {
        const targetOffererId =
          offerResponse?.venue.managingOfferer.id || offererId
        const responses = await Promise.all([
          api.listEducationalDomains(),
          api.listEducationalOfferers(targetOffererId),
          api.getNationalPrograms(),
        ])

        const [
          domainsResponse,
          { educationalOfferers },
          nationalProgramsResponse,
        ] = responses

        const domains = domainsResponse.map((domain) => ({
          value: domain.id.toString(),
          label: domain.name,
        }))

        const offerersResponse =
          serializeEducationalOfferers(educationalOfferers)

        const nationalPrograms = nationalProgramsResponse.map(
          (nationalProgram) => ({
            label: nationalProgram.name,
            value: nationalProgram.id,
          })
        )

        const offerers = getUserOfferersFromOffer(offerersResponse, offer)

        setData({
          offerers,
          domains,
          nationalPrograms,
        })

        setIsReady(true)
      } catch (e) {
        notify.error(GET_DATA_ERROR_MESSAGE)
      }
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
