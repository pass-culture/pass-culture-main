import { useNavigate } from 'react-router'
import useSWR from 'swr'

import { api } from '@/apiClient/api'
import type { CollectiveOfferTemplateResponseModel } from '@/apiClient/v1'
import { BasicLayout } from '@/app/App/layouts/BasicLayout/BasicLayout'
import {
  DEFAULT_COLLECTIVE_SEARCH_FILTERS,
  DEFAULT_PAGE,
} from '@/commons/core/Offers/constants'
import { useCollectiveOffersSwrKeys } from '@/commons/core/Offers/hooks/useCollectiveOffersSwrKeys'
import { useQueryCollectiveSearchFilters } from '@/commons/core/Offers/hooks/useQuerySearchFilters'
import type { CollectiveSearchFiltersParams } from '@/commons/core/Offers/types'
import { computeCollectiveOffersUrl } from '@/commons/core/Offers/utils/computeCollectiveOffersUrl'
import { serializeApiCollectiveFilters } from '@/commons/core/Offers/utils/serializeApiCollectiveFilters'
import { useAppSelector } from '@/commons/hooks/useAppSelector'
import { ensureCurrentOfferer } from '@/commons/store/offerer/selectors'
import { TemplateCollectiveOffersScreen } from '@/pages/TemplateCollectiveOffers/TemplateCollectiveOffersScreen/TemplateCollectiveOffersScreen'
import { Spinner } from '@/ui-kit/Spinner/Spinner'

export const TemplateCollectiveOffers = (): JSX.Element => {
  const urlSearchFilters = useQueryCollectiveSearchFilters()
  const selectedOffererId = useAppSelector(ensureCurrentOfferer).id

  const currentPageNumber = urlSearchFilters.page ?? DEFAULT_PAGE
  const navigate = useNavigate()

  const redirectWithUrlFilters = (
    filters: Partial<CollectiveSearchFiltersParams>
  ) => {
    // We dont need to pass the offererId in the URL since
    // its already present in the redux store (useSelector(selectCurrentOffererId))
    delete filters.offererId

    // eslint-disable-next-line @typescript-eslint/no-floating-promises
    navigate(
      computeCollectiveOffersUrl(
        filters,
        DEFAULT_COLLECTIVE_SEARCH_FILTERS,
        true
      ),
      { replace: true }
    )
  }

  const [queryKey, apiFilters] = useCollectiveOffersSwrKeys({
    isInTemplateOffersPage: true,
  })

  const offersQuery = useSWR<CollectiveOfferTemplateResponseModel[]>(
    [queryKey, apiFilters],
    () => {
      const params = serializeApiCollectiveFilters(apiFilters)
      return api.getCollectiveOfferTemplates(
        params.name,
        params.offererId,
        params.status,
        params.venueId,
        params.periodBeginningDate,
        params.periodEndingDate,
        params.format,
        params.locationType,
        params.offererAddressId
      )
    },
    { fallbackData: [] }
  )

  return (
    <BasicLayout mainHeading="Offres vitrines">
      {offersQuery.isLoading ? (
        <Spinner />
      ) : (
        <TemplateCollectiveOffersScreen
          currentPageNumber={currentPageNumber}
          initialSearchFilters={apiFilters}
          isLoading={offersQuery.isLoading}
          offererId={selectedOffererId.toString()}
          offers={offersQuery.data ?? []}
          redirectWithUrlFilters={redirectWithUrlFilters}
          urlSearchFilters={urlSearchFilters}
        />
      )}
    </BasicLayout>
  )
}

// Lazy-loaded by react-router
// ts-unused-exports:disable-next-line
export const Component = TemplateCollectiveOffers
