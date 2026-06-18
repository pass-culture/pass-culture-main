import { useNavigate } from 'react-router'
import { useSWRConfig } from 'swr'

import { api } from '@/apiClient/api'
import { isErrorAPIError } from '@/apiClient/helpers'
import type { CollectiveStockEditionBodyModel } from '@/apiClient/v1'
import { GET_COLLECTIVE_OFFER_QUERY_KEY } from '@/commons/config/swrQueryKeys'
import { Mode } from '@/commons/core/OfferEducational/types'
import { PATCH_SUCCESS_MESSAGE } from '@/commons/core/shared/constants'
import { useActiveFeature } from '@/commons/hooks/useActiveFeature'
import { useSnackBar } from '@/commons/hooks/useSnackBar'
import { useSyncVenueCache } from '@/commons/hooks/useSyncVenueCache'
import { isCollectiveStockEditable } from '@/commons/utils/isActionAllowedOnCollectiveOffer'
import { BannerPublicApi } from '@/components/BannerPublicApi/BannerPublicApi'
import { CollectiveStatusLabel } from '@/components/CollectiveStatusLabel/CollectiveStatusLabel'
import { CollectiveOfferLayout } from '@/pages/CollectiveOffer/CollectiveOfferLayout/CollectiveOfferLayout'

import {
  type CollectiveOfferFromParamsProps,
  withOnlyCollectiveOfferFromParams,
} from '../../CollectiveOffer/components/OfferEducational/useCollectiveOfferFromParams'
import { OfferEducationalStock } from '../components/OfferEducationalStock/OfferEducationalStock'
import styles from './CollectiveOfferStockEdition.module.scss'

export const CollectiveOfferStockEdition = ({
  offer,
}: CollectiveOfferFromParamsProps): JSX.Element => {
  const snackBar = useSnackBar()
  const navigate = useNavigate()
  const { mutate } = useSWRConfig()
  const { syncVenue } = useSyncVenueCache()
  const isNewCollectivePriceEnabled = useActiveFeature(
    'WIP_ENABLE_NEW_COLLECTIVE_PRICE_DETAILS'
  )

  const departementCode = offer.venue.departementCode ?? ''

  const handleSubmitStock = async (
    newCollectiveStock: CollectiveStockEditionBodyModel
  ) => {
    if (isNewCollectivePriceEnabled) {
      delete newCollectiveStock.priceDetail
    }
    if (!offer.collectiveStock) {
      return snackBar.error('Impossible de mettre à jour le stock.')
    }
    try {
      await api.editCollectiveStock({
        path: { collective_stock_id: offer.collectiveStock.id },
        body: newCollectiveStock,
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

    const nextStep = `/offre/${offer.id}/collectif/recapitulatif`
    navigate(nextStep)
    snackBar.success(PATCH_SUCCESS_MESSAGE)
  }
  const stockCanBeEdited = isCollectiveStockEditable(offer)

  return (
    <CollectiveOfferLayout
      offer={offer}
      subTitle={offer.name}
      isTemplate={false}
    >
      <div className={styles['actions']}>
        <CollectiveStatusLabel offerDisplayedStatus={offer.displayedStatus} />
      </div>
      {offer.isPublicApi && (
        <BannerPublicApi className={styles['banner-space']} />
      )}
      <OfferEducationalStock
        initialStock={offer.collectiveStock ?? {}}
        departementCode={departementCode}
        mode={stockCanBeEdited ? Mode.EDITION : Mode.READ_ONLY}
        allowedActions={offer.allowedActions}
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
