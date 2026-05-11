import { useAppSelector } from '@/commons/hooks/useAppSelector'
import { ensureSelectedPartnerVenue } from '@/commons/store/user/selectors'
import { useStoredFilterConfig } from '@/components/OffersTableSearch/utils'

import type { CollectiveSearchFiltersParams } from '../types'
import { getCollectiveOffersSwrKeys } from '../utils/getCollectiveOffersSwrKeys'
import { useQueryCollectiveSearchFilters } from './useQuerySearchFilters'

type UseCollectiveOffersSwrKeysProps = {
  isInTemplateOffersPage: boolean
}

/**
 * SSOT for collective offers list SWR key.
 *
 * The list fetched in `CollectiveOffers` and `TemplateCollectiveOffers` MUST agree on the same mutation keys.
 */
export function useCollectiveOffersSwrKeys({
  isInTemplateOffersPage,
}: UseCollectiveOffersSwrKeysProps): [string, CollectiveSearchFiltersParams] {
  const urlSearchFilters = useQueryCollectiveSearchFilters()
  const { storedFilters } = useStoredFilterConfig(
    isInTemplateOffersPage ? 'template' : 'collective'
  )
  const selectedPartnerVenue = useAppSelector(ensureSelectedPartnerVenue)

  const mergedSearchFilters: Partial<CollectiveSearchFiltersParams> = {
    ...(storedFilters as Partial<CollectiveSearchFiltersParams>),
    ...urlSearchFilters,
  }

  return getCollectiveOffersSwrKeys({
    isInTemplateOffersPage,
    urlSearchFilters: mergedSearchFilters,
    selectedVenueId: selectedPartnerVenue.id,
  })
}
