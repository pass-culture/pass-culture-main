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
import { IndividualOfferLayout } from '@/components/IndividualOfferLayout/IndividualOfferLayout'

import { ProductBanner } from '../components/ProductBanner/ProductBanner'
import { SynchronizedBanner } from '../components/SynchronizedBanner/SynchronizedBanner'
import { useIndividualOfferImageUpload } from './commons/useIndividualOfferImageUpload'
import { DetailsEanSearch } from './components/DetailsEanSearch/DetailsEanSearch'
import { DetailsForm } from './components/DetailsForm/DetailsForm'

const IndividualOfferDescription = (): JSX.Element | null => {
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
    <IndividualOfferLayout offer={offer}>
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
    </IndividualOfferLayout>
  )
}

// Below exports are used by react-router
// ts-unused-exports:disable-next-line
export const Component = IndividualOfferDescription
