import { useNavigate } from 'react-router'
import { useSWRConfig } from 'swr'

import { apiNew } from '@/apiClient/api'
import { isErrorAPIError } from '@/apiClient/helpers'
import type { GetCollectiveOfferResponseModel } from '@/apiClient/v1/new'
import { GET_COLLECTIVE_OFFER_QUERY_KEY } from '@/commons/config/swrQueryKeys'
import {
  Mode,
  type OfferEducationalStockFormValues,
} from '@/commons/core/OfferEducational/types'
import { computeURLCollectiveOfferId } from '@/commons/core/OfferEducational/utils/computeURLCollectiveOfferId'
import { createPatchStockDataPayload } from '@/commons/core/OfferEducational/utils/createPatchStockDataPayload'
import { extractInitialStockValues } from '@/commons/core/OfferEducational/utils/extractInitialStockValues'
import { PATCH_SUCCESS_MESSAGE } from '@/commons/core/shared/constants'
import { useSnackBar } from '@/commons/hooks/useSnackBar'
import { useSyncVenueCache } from '@/commons/hooks/useSyncVenueCache'
import { isCollectiveStockEditable } from '@/commons/utils/isActionAllowedOnCollectiveOffer'
import { CollectiveOfferLayout } from '@/pages/CollectiveOffer/CollectiveOfferLayout/CollectiveOfferLayout'

import {
  type CollectiveOfferFromParamsProps,
  withOnlyCollectiveOfferFromParams,
} from '../../CollectiveOffer/components/OfferEducational/useCollectiveOfferFromParams'
import { OfferEducationalStock } from '../components/OfferEducationalStock/OfferEducationalStock'

export const CollectiveOfferStockEdition = ({
  offer,
}: CollectiveOfferFromParamsProps): JSX.Element => {
  const snackBar = useSnackBar()
  const navigate = useNavigate()
  const { mutate } = useSWRConfig()
  const { syncVenue } = useSyncVenueCache()

  const initialValues = extractInitialStockValues(offer)

  const handleSubmitStock = async (
    offer: GetCollectiveOfferResponseModel,
    values: OfferEducationalStockFormValues
  ) => {
    if (!offer.collectiveStock) {
      return snackBar.error('Impossible de mettre à jour le stock.')
    }

    const stockPayload = createPatchStockDataPayload(
      values,
      offer.venue.departementCode ?? '',
      initialValues
    )
    try {
      await apiNew.editCollectiveStock({
        path: { collective_stock_id: offer.collectiveStock.id },
        body: stockPayload,
      })
    } catch (error) {
      if (isErrorAPIError(error) && error.status < 500) {
        throw error
      }
      snackBar.error(
        'Une erreur est survenue lors de la mise à jour de votre stock.'
      )
      return
    }

    await mutate([GET_COLLECTIVE_OFFER_QUERY_KEY, offer.id])
    await syncVenue(offer.venue.id)

    // eslint-disable-next-line @typescript-eslint/no-floating-promises
    navigate(
      `/offre/${computeURLCollectiveOfferId(
        offer.id,
        false
      )}/collectif/recapitulatif`
    )
    snackBar.success(PATCH_SUCCESS_MESSAGE)
  }
  const stockCanBeEdited = isCollectiveStockEditable(offer)

  return (
    <CollectiveOfferLayout
      offer={offer}
      subTitle={offer.name}
      isTemplate={false}
    >
      <OfferEducationalStock
        initialValues={initialValues}
        mode={stockCanBeEdited ? Mode.EDITION : Mode.READ_ONLY}
        offer={offer}
        onSubmit={handleSubmitStock}
      />
    </CollectiveOfferLayout>
  )
}

// Lazy-loaded by react-router
// ts-unused-exports:disable-next-line
export const Component = withOnlyCollectiveOfferFromParams(
  CollectiveOfferStockEdition
)
