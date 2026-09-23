import { useEffect, useId, useState } from 'react'

import { DisplayableActivity } from '@/apiClient/v1'
import { useIndividualOfferContext } from '@/commons/context/IndividualOfferContext/IndividualOfferContext'
import {
  CULTURAL_OUTREACH_ALLOWED_ACTIVITIES,
  OFFER_WIZARD_MODE,
} from '@/commons/core/Offers/constants'
import type { OfferExtraData } from '@/commons/core/Offers/types'
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
import type {
  DetailsFormValues,
  Product,
} from '@/pages/IndividualOffer/IndividualOfferDescription/commons/types'
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
  const extraData = initialOffer?.extraData as OfferExtraData | undefined
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

  const hasSelectedProduct = !!initialValues.productId
  const isDraftOfferNotProductBased = isNewOfferDraft && !hasSelectedProduct

  const selectedSubcategoryId = subcategoryId
  const [subcatError, setSubcatError] = useState<string | undefined>(undefined)

  useEffect(() => {
    if (
      isDraftOfferNotProductBased &&
      isSubCategoryCD(selectedSubcategoryId ?? '')
    ) {
      setSubcatError('Les offres de type CD doivent être liées à un produit.')
    } else {
      setSubcatError(undefined)
    }
  }, [isDraftOfferNotProductBased, selectedSubcategoryId])

  const isEanSearchAvailable =
    selectedPartnerVenue.activity === DisplayableActivity.RECORD_STORE

  const canClaimCulturalOutreach =
    isCulturalOutreachEnabled &&
    selectedPartnerVenue.activity !== null &&
    CULTURAL_OUTREACH_ALLOWED_ACTIVITIES.has(selectedPartnerVenue.activity)

  const isEanSearchInputDisplayed =
    isEanSearchAvailable && mode === OFFER_WIZARD_MODE.CREATION

  const updateProduct = (ean: string, product: Product) => {
    const { description, gtlId, subcategoryId, images, ...restProduct } =
      product
    const subcategory = subCategories.find((s) => s.id === subcategoryId)
    if (!subcategory) {
      return handleUnexpectedError(
        new FrontendError('Unknown or missing `subcategoryId`.')
      )
    }

    const { categoryId, conditionalFields } = subcategory

    const imageUrl = images.recto
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
      ean,
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

  return (
    <>
      {isOfferProductBasedButNotSynchronized(initialOffer) && <ProductBanner />}
      {isOfferSynchronized(initialOffer) && (
        <SynchronizedBanner providerName={initialOffer?.lastProvider?.name} />
      )}
      <FormLayout.MandatoryInfo />

      {isEanSearchInputDisplayed && (
        <DetailsEanSearch
          isDraftOffer={isNewOfferDraft}
          initialEan={extraData?.ean}
          isProductBased={hasSelectedProduct}
          onEanReset={() => {
            handleEanImage()
            setInitialValues(getInitialValues())
          }}
          onEanSearch={updateProduct}
          subcatError={subcatError}
        />
      )}

      <DetailsForm
        key={initialValues.productId}
        initialValues={initialValues}
        setSubcategoryId={setSubcategoryId}
        filteredCategories={categories}
        filteredSubcategories={subCategories}
        isEanSearchDisplayed={isEanSearchInputDisplayed}
        canClaimCulturalOutreach={canClaimCulturalOutreach}
      />
    </>
  )
}
