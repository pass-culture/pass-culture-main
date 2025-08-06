import { yupResolver } from '@hookform/resolvers/yup'
import { FormProvider, useForm } from 'react-hook-form'
import { useLocation, useNavigate } from 'react-router'
import { useSWRConfig } from 'swr'

import { api } from '@/apiClient//api'
import { isErrorAPIError } from '@/apiClient//helpers'
import {
  CreateThumbnailResponseModel,
  GetIndividualOfferWithAddressResponseModel,
} from '@/apiClient//v1'
import { useAnalytics } from '@/app/App/analytics/firebase'
import { GET_OFFER_QUERY_KEY } from '@/commons/config/swrQueryKeys'
import { Events } from '@/commons/core/FirebaseEvents/constants'
import {
  INDIVIDUAL_OFFER_WIZARD_STEP_IDS,
  OFFER_WIZARD_MODE,
} from '@/commons/core/Offers/constants'
import { getIndividualOfferUrl } from '@/commons/core/Offers/utils/getIndividualOfferUrl'
import { isOfferDisabled } from '@/commons/core/Offers/utils/isOfferDisabled'
import { isOfferProductBased } from '@/commons/core/Offers/utils/typology'
import { useOfferWizardMode } from '@/commons/hooks/useOfferWizardMode'
import { UploaderModeEnum } from '@/commons/utils/imageUploadTypes'
import { FormLayout } from '@/components/FormLayout/FormLayout'
import { ImageDragAndDropUploader } from '@/components/ImageDragAndDropUploader/ImageDragAndDropUploader'
import { getIndividualOfferImage } from '@/components/IndividualOffer/utils/getIndividualOfferImage'
import { RouteLeavingGuardIndividualOffer } from '@/components/RouteLeavingGuardIndividualOffer/RouteLeavingGuardIndividualOffer'
import { ScrollToFirstHookFormErrorAfterSubmit } from '@/components/ScrollToFirstErrorAfterSubmit/ScrollToFirstErrorAfterSubmit'
import { ActionBar } from '@/pages/IndividualOffer/components/ActionBar/ActionBar'
import { useIndividualOfferImageUpload } from '@/pages/IndividualOffer/IndividualOfferDetails/commons/useIndividualOfferImageUpload'
import { Divider } from '@/ui-kit/Divider/Divider'
import { TextInput } from '@/ui-kit/form/TextInput/TextInput'

import { buildInitialValues } from '../commons/buildInitialValues'
import { IndividualOfferMediaFormValues } from '../commons/types'
import { getValidationSchema } from '../commons/validationSchema'
import styles from './IndividualOfferMediaScreen.module.scss'
import { VideoUploaderTips } from './VideoUploaderOfferTips/VideoUploaderOfferTips'

export type IndividualOfferMediaScreenProps = {
  offer: GetIndividualOfferWithAddressResponseModel
}

export const IndividualOfferMediaScreen = ({
  offer,
}: IndividualOfferMediaScreenProps): JSX.Element => {
  const { logEvent } = useAnalytics()
  const { mutate } = useSWRConfig()
  const navigate = useNavigate()
  const { pathname } = useLocation()
  const isOnboarding = pathname.indexOf('onboarding') !== -1
  const mode = useOfferWizardMode()

  const initialImageOffer = getIndividualOfferImage(offer)
  const {
    displayedImage,
    hasUpsertedImage,
    onImageDelete,
    onImageUpload,
    handleImageOnSubmit,
  } = useIndividualOfferImageUpload(initialImageOffer)

  const isProductBased = isOfferProductBased(offer)

  const form = useForm<IndividualOfferMediaFormValues>({
    defaultValues: { videoUrl: offer.videoUrl ?? '' },
    resolver: yupResolver<IndividualOfferMediaFormValues>(
      getValidationSchema()
    ),
    mode: 'onBlur',
  })

  const isFormDirty = form.formState.isDirty || hasUpsertedImage

  const handlePreviousStep = async () => {
    if (mode === OFFER_WIZARD_MODE.CREATION) {
      await navigate(
        getIndividualOfferUrl({
          offerId: offer.id,
          step: INDIVIDUAL_OFFER_WIZARD_STEP_IDS.USEFUL_INFORMATIONS,
          mode: OFFER_WIZARD_MODE.CREATION,
          isOnboarding,
        })
      )
    } else {
      await navigate(
        getIndividualOfferUrl({
          offerId: offer.id,
          step: INDIVIDUAL_OFFER_WIZARD_STEP_IDS.MEDIA,
          mode: OFFER_WIZARD_MODE.READ_ONLY,
          isOnboarding,
        })
      )
    }
  }

  const onSubmit = async (formValues: IndividualOfferMediaFormValues) => {
    try {
      // If only videoUrl was updated, there is an inner control on the
      // definition of handleImageOnSubmit so thumbnail associated requests cannot be made
      // if hasUpsertedImage=false.
      if (isFormDirty) {
        // Images can never be uploaded for product-based offers,
        // the drag & drop should not be enabled so this is a safeguard.
        if (!isProductBased) {
          await mutate(
            [GET_OFFER_QUERY_KEY, offer.id],
            handleImageOnSubmit(offer.id),
            {
              revalidate: false,
              populateCache: (
                thumbnailResult: CreateThumbnailResponseModel | void,
                offer
              ) => {
                // If defined, the result comes from a thumbnail
                // creation. Otherwise, its a result from a deletion.
                if (thumbnailResult) {
                  return {
                    ...offer,
                    thumbUrl: thumbnailResult.url,
                  }
                } else {
                  return {
                    ...offer,
                    thumbUrl: '',
                  }
                }
              },
            }
          )
        }

        await mutate(
          [GET_OFFER_QUERY_KEY, offer.id],
          api.patchDraftOffer(offer.id, {
            videoUrl: formValues.videoUrl,
          }),
          {
            revalidate: false,
          }
        )
      }

      let nextStep = INDIVIDUAL_OFFER_WIZARD_STEP_IDS.MEDIA
      if (mode !== OFFER_WIZARD_MODE.EDITION) {
        nextStep = offer.isEvent
          ? INDIVIDUAL_OFFER_WIZARD_STEP_IDS.TARIFS
          : INDIVIDUAL_OFFER_WIZARD_STEP_IDS.STOCKS
      }

      await navigate(
        getIndividualOfferUrl({
          offerId: offer.id,
          step: nextStep,
          mode:
            mode === OFFER_WIZARD_MODE.EDITION
              ? OFFER_WIZARD_MODE.READ_ONLY
              : mode,
          isOnboarding,
        })
      )
    } catch (error) {
      if (!isErrorAPIError(error)) {
        return
      }
      for (const field in error.body) {
        form.setError(field as keyof IndividualOfferMediaFormValues, {
          message: error.body[field],
        })
      }
    }
  }

  const logOnImageDropOrSelected = () => {
    logEvent(Events.DRAG_OR_SELECTED_IMAGE, {
      imageType: UploaderModeEnum.OFFER,
      imageCreationStage: 'add image',
    })
  }

  return (
    <FormProvider {...form}>
      <form onSubmit={form.handleSubmit(onSubmit)}>
        <ScrollToFirstHookFormErrorAfterSubmit />
        <FormLayout>
          <FormLayout.MandatoryInfo />
          <FormLayout.Section title="Illustrez votre offre">
            <FormLayout.Row inline className={styles['media-row']}>
              <FormLayout.SubSection
                title="Ajoutez une image"
                className={styles['media-sub-section']}
              >
                <ImageDragAndDropUploader
                  onImageUpload={onImageUpload}
                  onImageDelete={onImageDelete}
                  initialValues={buildInitialValues(displayedImage)}
                  mode={UploaderModeEnum.OFFER}
                  onImageDropOrSelected={logOnImageDropOrSelected}
                  hideActionButtons={isProductBased}
                  disabled={isProductBased}
                />
              </FormLayout.SubSection>
              <Divider
                orientation="vertical"
                className={styles['media-divider']}
              />
              <FormLayout.SubSection
                title="Ajoutez une vidéo"
                isNew
                className={styles['media-sub-section']}
              >
                <TextInput
                  label="Lien URL Youtube"
                  className={styles['video-section-input']}
                  type="text"
                  description="Format : https://www.youtube.com/watch?v=0R5PZxOgoz8"
                  error={form.formState.errors.videoUrl?.message}
                  {...form.register('videoUrl')}
                />
                <VideoUploaderTips />
              </FormLayout.SubSection>
            </FormLayout.Row>
          </FormLayout.Section>
        </FormLayout>
        <ActionBar
          onClickPrevious={handlePreviousStep}
          step={INDIVIDUAL_OFFER_WIZARD_STEP_IDS.MEDIA}
          isDisabled={
            form.formState.isSubmitting || isOfferDisabled(offer.status)
          }
        />
        <RouteLeavingGuardIndividualOffer
          when={isFormDirty && !form.formState.isSubmitting}
        />
      </form>
    </FormProvider>
  )
}
