import { useState } from 'react'

import {
  DisplayableActivity,
  type GetProductInformations,
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
import { FrontendError } from '@/commons/errors/FrontendError'
import { handleUnexpectedError } from '@/commons/errors/handleUnexpectedError'
import { useActiveFeature } from '@/commons/hooks/useActiveFeature'
import { useAppSelector } from '@/commons/hooks/useAppSelector'
import { useOfferWizardMode } from '@/commons/hooks/useOfferWizardMode'
import { ensureSelectedPartnerVenue } from '@/commons/store/user/selectors'
import { FormLayout } from '@/components/FormLayout/FormLayout'
import type { DetailsFormValues } from '@/pages/IndividualOffer/IndividualOfferDescription/commons/types'
import { useIndividualOfferImageUpload } from '@/pages/IndividualOffer/IndividualOfferDescription/commons/useIndividualOfferImageUpload'
import {
  getInitialValuesFromOffer,
  getInitialValuesFromVenue,
  hasMusicType,
  isSubCategoryCD,
} from '@/pages/IndividualOffer/IndividualOfferDescription/commons/utils'

import { ProductBanner } from '../../components/ProductBanner/ProductBanner'
import { SynchronizedBanner } from '../../components/SynchronizedBanner/SynchronizedBanner'
import { DetailsEanSearch } from './DetailsEanSearch/DetailsEanSearch'
import { DetailsForm } from './DetailsForm/DetailsForm'

export const IndividualOfferDescriptionScreen = () => {
  const isCulturalOutreachEnabled = useActiveFeature(
    'WIP_ENABLE_CULTURAL_OUTREACH'
  )

  const {
    categories,
    subCategories,
    offer: initialOffer,
  } = useIndividualOfferContext()
  const isNewOfferDraft = !initialOffer
  const mode = useOfferWizardMode()
  const selectedPartnerVenue = useAppSelector(ensureSelectedPartnerVenue)

  const initialOfferImage = getIndividualOfferImage(initialOffer)
  const { handleEanImage } = useIndividualOfferImageUpload(initialOfferImage)

  const getInitialValues = () => {
    return isNewOfferDraft
      ? getInitialValuesFromVenue(selectedPartnerVenue)
      : getInitialValuesFromOffer({
          offer: initialOffer,
          subcategories: subCategories,
        })
  }
  const [initialValues, setInitialValues] = useState<DetailsFormValues>(
    getInitialValues()
  )
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
      setInitialValues(getInitialValues())
      return
    }

    const { description, gtlId, subcategoryId, images, ...restProduct } =
      product
    const subcategory = subCategories.find((s) => s.id === subcategoryId)
    if (!subcategory) {
      return handleUnexpectedError(
        new FrontendError('Unknown or missing `subcategoryId`.')
      )
    }

    const { categoryId, conditionalFields } = subcategory

    // TODO(mdesquilbet, 2026-09-30): Update model in backend (and migrate it to Pydantic v2)
    const imageUrl = images.recto as string | null
    if (imageUrl) {
      handleEanImage(imageUrl)
    }

    let gtl_id = ''
    if (hasMusicType(categoryId, conditionalFields)) {
      // Fallback to "Autre" in case of missing gtlId
      // to define "Genre musical" when relevant.
      gtl_id = gtlId || '19000000'
    }

    setInitialValues((prevInitialValues) => ({
      ...prevInitialValues,
      ...restProduct,
      description: description || '',
      categoryId,
      subcategoryId,
      gtl_id,
      subcategoryConditionalFields: conditionalFields as Array<
        keyof DetailsFormValues
      >,
      productId: restProduct.id.toString(),
    }))
  }

  const product = {
    ean: initialOffer?.extraData?.ean,
    id: initialValues.productId,
  } as Partial<GetProductInformations>

  return (
    <>
      {isOfferProductBasedButNotSynchronized(initialOffer) && <ProductBanner />}
      {isOfferSynchronized(initialOffer) && (
        <SynchronizedBanner providerName={initialOffer?.lastProvider?.name} />
      )}
      <FormLayout.MandatoryInfo />

      {isEanSearchInputDisplayed && (
        <DetailsEanSearch
          product={product}
          onProductChange={updateProduct}
          disabled={!!initialValues.productId}
          required={isSubCategoryCD(subcategoryId ?? '')}
          canClearProduct={isNewOfferDraft}
        />
      )}

      <DetailsForm
        key={initialValues.productId}
        initialValues={initialValues}
        onSubcategoryChange={setSubcategoryId}
        filteredCategories={categories}
        filteredSubcategories={subCategories}
        isEanSearchDisplayed={isEanSearchInputDisplayed}
        canClaimCulturalOutreach={canClaimCulturalOutreach}
      />
    </>
  )
}
