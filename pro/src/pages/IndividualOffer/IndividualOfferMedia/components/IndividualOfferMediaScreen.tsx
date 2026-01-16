import { FormProvider, useForm } from 'react-hook-form'
import { useLocation, useNavigate } from 'react-router'
import { useSWRConfig } from 'swr'

import { isErrorAPIError } from '@/apiClient/helpers'
import type {
  CreateThumbnailResponseModel,
  GetIndividualOfferWithAddressResponseModel,
} from '@/apiClient/v1'
import { useAnalytics } from '@/app/App/analytics/firebase'
import { GET_OFFER_QUERY_KEY } from '@/commons/config/swrQueryKeys'
import { Events } from '@/commons/core/FirebaseEvents/constants'
import {
  INDIVIDUAL_OFFER_WIZARD_STEP_IDS,
  OFFER_WIZARD_MODE,
} from '@/commons/core/Offers/constants'
import { getIndividualOfferImage } from '@/commons/core/Offers/utils/getIndividualOfferImage'
import { getIndividualOfferUrl } from '@/commons/core/Offers/utils/getIndividualOfferUrl'
import { isOfferDisabled } from '@/commons/core/Offers/utils/isOfferDisabled'
import { isOfferProductBased } from '@/commons/core/Offers/utils/typology'
import { useOfferWizardMode } from '@/commons/hooks/useOfferWizardMode'
import { UploaderModeEnum } from '@/commons/utils/imageUploadTypes'
import { FormLayout } from '@/components/FormLayout/FormLayout'
import { ImageDragAndDropUploader } from '@/components/ImageDragAndDropUploader/ImageDragAndDropUploader'
import { RouteLeavingGuardIndividualOffer } from '@/components/RouteLeavingGuardIndividualOffer/RouteLeavingGuardIndividualOffer'
import { VideoUploader } from '@/components/VideoUploader/VideoUploader'
import { ActionBar } from '@/pages/IndividualOffer/components/ActionBar/ActionBar'
import { useIndividualOfferImageUpload } from '@/pages/IndividualOffer/IndividualOfferDetails/commons/useIndividualOfferImageUpload'
import { Divider } from '@/ui-kit/Divider/Divider'

import { buildInitialValues } from '../commons/buildInitialValues'
import { useVideoUploaderContext } from '../commons/context/VideoUploaderContext/VideoUploaderContext'
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

  const { handleVideoOnSubmit, videoUrl, videoData } = useVideoUploaderContext()

  const isProductBased = isOfferProductBased(offer)

  const form = useForm()

  const hasUpdatedVideoUrl = videoUrl !== offer.videoData.videoUrl
  const isFormDirty = hasUpdatedVideoUrl || hasUpsertedImage

  const handlePreviousStep = async () => {
    if (mode === OFFER_WIZARD_MODE.CREATION) {
      await navigate(
        getIndividualOfferUrl({
          offerId: offer.id,
          step: INDIVIDUAL_OFFER_WIZARD_STEP_IDS.LOCATION,
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

  const onSubmit = async () => {
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
                // FIXME: in cache we update both offer.activeMediation and offer.thumbUrl
                // properties, depending on the type of offer, one or another is actually updated
                // (aka. getIndividualOfferImage) but we'd like an unique way to store this information.
                if (thumbnailResult) {
                  return {
                    ...(offer || {}),
                    thumbUrl: thumbnailResult.url,
                    activeMediation: {
                      ...(offer?.activeMediation || {}),
                      thumbUrl: thumbnailResult.url,
                      credit: thumbnailResult.credit,
                    },
                  }
                } else {
                  return {
                    ...(offer || {}),
                    thumbUrl: '',
                    activeMediation: {
                      ...(offer?.activeMediation || {}),
                      thumbUrl: '',
                      credit: '',
                    },
                  }
                }
              },
            }
          )
        }

        if (hasUpdatedVideoUrl) {
          await mutate([GET_OFFER_QUERY_KEY, offer.id], handleVideoOnSubmit(), {
            revalidate: false,
          })
        }
      }

      let nextStep = INDIVIDUAL_OFFER_WIZARD_STEP_IDS.MEDIA
      if (mode !== OFFER_WIZARD_MODE.EDITION) {
        nextStep = INDIVIDUAL_OFFER_WIZARD_STEP_IDS.TARIFS
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
        <FormLayout>
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
                <VideoUploader />
                {!videoData?.videoThumbnailUrl && <VideoUploaderTips />}
              </FormLayout.SubSection>
            </FormLayout.Row>
          </FormLayout.Section>
        </FormLayout>
        <ActionBar
          onClickPrevious={handlePreviousStep}
          step={INDIVIDUAL_OFFER_WIZARD_STEP_IDS.MEDIA}
          isDisabled={form.formState.isSubmitting || isOfferDisabled(offer)}
        />
        <RouteLeavingGuardIndividualOffer
          when={isFormDirty && !form.formState.isSubmitting}
        />
      </form>
    </FormProvider>
  )
}
