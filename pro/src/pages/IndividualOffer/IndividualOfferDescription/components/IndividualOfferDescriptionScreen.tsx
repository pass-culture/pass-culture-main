import { useState } from 'react'

import {
  DisplayableActivity,
  type GetProductInformations,
  SubcategoryIdEnum,
} from '@/apiClient/v1'
import { useIndividualOfferContext } from '@/commons/context/IndividualOfferContext/IndividualOfferContext'
import {
  CULTURAL_OUTREACH_ALLOWED_ACTIVITIES,
  OFFER_WIZARD_MODE,
} from '@/commons/core/Offers/constants'
import { getIndividualOfferImage } from '@/commons/core/Offers/utils/getIndividualOfferImage'
import {
  isOfferProductBasedButNotSynchronized,
  isOfferSynchronized,
} from '@/commons/core/Offers/utils/typology'
import { useActiveFeature } from '@/commons/hooks/useActiveFeature'
import { useAppSelector } from '@/commons/hooks/useAppSelector'
import { useOfferWizardMode } from '@/commons/hooks/useOfferWizardMode'
import { ensureSelectedPartnerVenue } from '@/commons/store/user/selectors'
import { FormLayout } from '@/components/FormLayout/FormLayout'
import { useIndividualOfferImageUpload } from '@/pages/IndividualOffer/IndividualOfferDescription/commons/useIndividualOfferImageUpload'

import { ProductBanner } from '../../components/ProductBanner/ProductBanner'
import { SynchronizedBanner } from '../../components/SynchronizedBanner/SynchronizedBanner'
import { DetailsEanSearch } from './DetailsEanSearch/DetailsEanSearch'
import { DetailsForm } from './DetailsForm/DetailsForm'

export const IndividualOfferDescriptionScreen = () => {
  const isCulturalOutreachEnabled = useActiveFeature(
    'WIP_ENABLE_CULTURAL_OUTREACH'
  )

  const { offer } = useIndividualOfferContext()
  const [product, setProduct] = useState<GetProductInformations | undefined>()
  const isNewOfferDraft = !offer
  const mode = useOfferWizardMode()
  const selectedPartnerVenue = useAppSelector(ensureSelectedPartnerVenue)

  const initialOfferImage = getIndividualOfferImage(offer)
  const { handleEanImage } = useIndividualOfferImageUpload(initialOfferImage)

  const [subcategoryId, setSubcategoryId] = useState<string | undefined>(
    undefined
  )

  const isEanSearchAvailable =
    selectedPartnerVenue.activity === DisplayableActivity.RECORD_STORE

  const canClaimCulturalOutreach =
    isCulturalOutreachEnabled &&
    selectedPartnerVenue.activity !== null &&
    CULTURAL_OUTREACH_ALLOWED_ACTIVITIES.has(selectedPartnerVenue.activity)

  const isEanSearchInputDisplayed =
    isEanSearchAvailable && mode === OFFER_WIZARD_MODE.CREATION

  const updateProduct = (product: GetProductInformations | null) => {
    if (!product) {
      handleEanImage()
      setProduct(undefined)
      return
    }

    // TODO(mdesquilbet, 2026-09-30): Update model in backend (and migrate it to Pydantic v2)
    const imageUrl = product.images.recto as string | null
    if (imageUrl) {
      handleEanImage(imageUrl)
    }

    setProduct(product)
  }

  return (
    <>
      {isOfferProductBasedButNotSynchronized(offer) && <ProductBanner />}
      {isOfferSynchronized(offer) && (
        <SynchronizedBanner providerName={offer?.lastProvider?.name} />
      )}
      <FormLayout.MandatoryInfo />

      {isEanSearchInputDisplayed && (
        <DetailsEanSearch
          productEan={product?.ean || offer?.extraData?.ean}
          onProductChange={updateProduct}
          disabled={!!product?.id || !!offer?.productId}
          required={
            subcategoryId === SubcategoryIdEnum.SUPPORT_PHYSIQUE_MUSIQUE_CD
          }
          canClearProduct={isNewOfferDraft}
        />
      )}

      <DetailsForm
        key={product?.id}
        product={product}
        onSubcategoryChange={setSubcategoryId}
        isEanSearchDisplayed={isEanSearchInputDisplayed}
        canClaimCulturalOutreach={canClaimCulturalOutreach}
      />
    </>
  )
}
