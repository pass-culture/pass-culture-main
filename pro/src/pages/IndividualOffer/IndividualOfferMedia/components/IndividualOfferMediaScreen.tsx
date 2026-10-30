import { useEffect, useId, useRef, useState } from 'react'
import { FormProvider, useForm } from 'react-hook-form'
import { useLocation, useNavigate } from 'react-router'
import { useSWRConfig } from 'swr'

import { getHumanReadableApiError } from '@/apiClient/helpers'
import type { GetIndividualOfferResponseModel } from '@/apiClient/v1'
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
import { isOfferProductBasedButNotSynchronized } from '@/commons/core/Offers/utils/typology'
import { useAppSelector } from '@/commons/hooks/useAppSelector'
import { useFormNavigationGuard } from '@/commons/hooks/useFormNavigationGuard/useFormNavigationGuard'
import { useOfferWizardMode } from '@/commons/hooks/useOfferWizardMode'
import { useSnackBar } from '@/commons/hooks/useSnackBar'
import { ensureSelectedPartnerVenue } from '@/commons/store/user/selectors'
import { UploaderModeEnum } from '@/commons/utils/imageUploadTypes'
import { withVenueHelpers } from '@/commons/utils/withVenueHelpers'
import { FormLayout } from '@/components/FormLayout/FormLayout'
import {
  ALLOWED_IMAGE_TYPES_TO_EXTENSIONS,
  MAX_FILE_SIZE,
  UPLOAD_IMAGE_MAX_RESOLUTION,
} from '@/components/ImageDragAndDrop/constants'
import { getImageDimensions } from '@/components/ImageDragAndDrop/getImageDimensions'
import { getImageFormat } from '@/components/ImageDragAndDrop/getImageFormat'
import {
  ModalImageUpsertOrEdit,
  type OnImageUploadArgs,
} from '@/components/ModalImageUpsertOrEdit/ModalImageUpsertOrEdit'
import { ImagePlaceholder } from '@/components/SafeImage/ImagePlaceholder/ImagePlaceholder'
import { SafeImage } from '@/components/SafeImage/SafeImage'
import { VideoUploader } from '@/components/VideoUploader/VideoUploader'
import { Button } from '@/design-system/Button/Button'
import {
  ButtonColor,
  ButtonSize,
  ButtonVariant,
} from '@/design-system/Button/types'
import { SimpleModal } from '@/design-system/SimpleModal/SimpleModal'
import { UploadZone } from '@/design-system/UploadZone/UploadZone'
import { getConditionsText } from '@/design-system/UploadZone/utils'
import fullEditIcon from '@/icons/full-edit.svg'
import fullTrashIcon from '@/icons/full-trash.svg'
import strokePictureIcon from '@/icons/stroke-picture.svg'
import strokeWarningIcon from '@/icons/stroke-warning.svg'
import { useIndividualOfferImageUpload } from '@/pages/IndividualOffer/commons/useIndividualOfferImageUpload'
import { getAfterSubmitPath } from '@/pages/IndividualOffer/commons/utils/getAfterSubmitPath'
import { ActionBar } from '@/pages/IndividualOffer/components/ActionBar/ActionBar'

import { ProductBanner } from '../../components/ProductBanner/ProductBanner'
import { buildInitialValues } from '../commons/buildInitialValues'
import { useVideoUploaderContext } from '../commons/context/VideoUploaderContext/VideoUploaderContext'
import styles from './IndividualOfferMediaScreen.module.scss'
import { VideoUploaderTips } from './VideoUploaderOfferTips/VideoUploaderOfferTips'

type IndividualOfferMediaScreenProps = {
  offer: GetIndividualOfferResponseModel
}

const IMAGE_CONDITIONS_TEXT = `${getConditionsText(
  ALLOWED_IMAGE_TYPES_TO_EXTENSIONS,
  MAX_FILE_SIZE
)} Résolution maximale : 80 mégapixels.`

const IMAGE_FORMAT_ERROR = 'Le format de l’image n’est pas valide'
const IMAGE_RESOLUTION_ERROR =
  "Image trop volumineuse. La résolution maximale acceptée est d'environ 80 millions de pixels (9000 x 9000 pixels)"

// UploadZone only checks the declared type and the weight of the file:
// the actual content format and the resolution are checked here.
const validateImage = async (
  file: File
): Promise<
  { image: File; error?: never } | { image?: never; error: string }
> => {
  try {
    const content = await file.arrayBuffer()
    const { width, height } = await getImageDimensions(file)

    if (getImageFormat(content) === null) {
      return { error: IMAGE_FORMAT_ERROR }
    }
    if (width * height > UPLOAD_IMAGE_MAX_RESOLUTION) {
      return { error: IMAGE_RESOLUTION_ERROR }
    }

    const image = new File([content], file.name, { type: file.type })
    return { image: Object.assign(image, { width, height }) }
  } catch {
    return { error: IMAGE_FORMAT_ERROR }
  }
}

export const IndividualOfferMediaScreen = ({
  offer,
}: IndividualOfferMediaScreenProps): JSX.Element => {
  const { logEvent } = useAnalytics()
  const { mutate } = useSWRConfig()
  const navigate = useNavigate()
  const { pathname } = useLocation()
  const isOnboarding = pathname.includes('onboarding')
  const mode = useOfferWizardMode()
  const selectedPartnerVenue = useAppSelector(ensureSelectedPartnerVenue)
  const isClosed = withVenueHelpers(selectedPartnerVenue).isClosed
  const tipsVideoUploaderId = useId()

  const initialImageOffer = getIndividualOfferImage(offer)
  const {
    displayedImage,
    hasUpsertedImage,
    onImageDelete,
    onImageUpload,
    handleImageOnSubmit,
  } = useIndividualOfferImageUpload(initialImageOffer)

  const uploadZoneId = useId()
  const editButtonId = useId()
  const uploadZoneRef = useRef<HTMLInputElement>(null)
  const editButtonRef = useRef<HTMLButtonElement>(null)

  const initialValues = buildInitialValues(displayedImage)
  const { croppedImageUrl, originalImageUrl, credit, alternativeText } =
    initialValues
  const [isModalImageOpen, setIsModalImageOpen] = useState(false)
  const [isDeleteImageOpen, setIsDeleteImageOpen] = useState(false)
  const [draftImage, setDraftImage] = useState<File | undefined>(undefined)
  const [draftCredit, setDraftCredit] = useState<string | undefined>(credit)
  const [draftAlternativeText, setDraftAlternativeText] = useState<
    string | undefined
  >(alternativeText)
  const [imageError, setImageError] = useState<string | undefined>(undefined)
  // Remounting the upload zone clears its errors.
  const [uploadZoneKey, setUploadZoneKey] = useState(0)

  useEffect(() => {
    setDraftCredit(credit)
  }, [credit])
  useEffect(() => {
    setDraftAlternativeText(alternativeText)
  }, [alternativeText])

  const { handleVideoOnSubmit, videoUrl, videoDescription, videoData } =
    useVideoUploaderContext()
  const snackBar = useSnackBar()
  // Read by `afterSubmitState` so the success message is shown once the
  // destination page (or this same page) has taken over, instead of racing with the navigation.
  const hasSavedOfferRef = useRef(false)

  const isProductBased = isOfferProductBasedButNotSynchronized(offer)
  const isImageReadOnly = isProductBased || isClosed
  const imageUrl = croppedImageUrl || originalImageUrl
  const hasImage = !!imageUrl

  const form = useForm()

  const hasUpdatedVideoUrl = videoUrl !== (offer.videoData.videoUrl ?? '')
  const hasUpdatedVideoDescription =
    videoDescription !== (offer.videoData.videoDescription ?? '')
  const hasUpdatedVideo = hasUpdatedVideoUrl || hasUpdatedVideoDescription
  const isFormDirty = hasUpdatedVideo || hasUpsertedImage

  const handlePreviousStep = async () => {
    await navigate(
      getIndividualOfferUrl({
        offerId: offer.id,
        step: INDIVIDUAL_OFFER_WIZARD_STEP_IDS.LOCATION,
        mode: OFFER_WIZARD_MODE.CREATION,
        isOnboarding,
      })
    )
  }

  const onSubmit = async (): Promise<boolean> => {
    // If only videoUrl was updated, there is an inner control on the
    // definition of handleImageOnSubmit so thumbnail associated requests cannot be made
    // if hasUpsertedImage=false.
    if (!isFormDirty) {
      return true
    }

    // Images can never be uploaded for product-based offers,
    // the drag & drop should not be enabled so this is a safeguard.
    if (!isProductBased) {
      try {
        await mutate(
          [GET_OFFER_QUERY_KEY, offer.id],
          handleImageOnSubmit(offer.id),
          {
            revalidate: false,
            populateCache: (thumbnailResult, offer) => {
              // If defined, the result comes from a thumbnail
              // creation. Otherwise, its a result from a deletion.
              // FIXME: in cache we update both offer.activeMediation and offer.thumbUrl
              // properties, depending on the type of offer, one or another is actually updated
              // (aka. getIndividualOfferImage) but we'd like an unique way to store this information.
              if (thumbnailResult) {
                return {
                  ...offer,
                  thumbUrl: thumbnailResult.url,
                  activeMediation: {
                    ...offer?.activeMediation,
                    thumbUrl: thumbnailResult.url,
                    credit: thumbnailResult.credit,
                    alternativeText: thumbnailResult.alternativeText,
                  },
                }
              } else {
                return {
                  ...offer,
                  thumbUrl: '',
                  activeMediation: {
                    ...offer?.activeMediation,
                    thumbUrl: '',
                    credit: '',
                    alternativeText: '',
                  },
                }
              }
            },
          }
        )
      } catch (error) {
        snackBar.error(
          getHumanReadableApiError(
            error,
            'Une erreur est survenue lors de l’enregistrement de votre image'
          )
        )
        return false
      }
    }

    if (hasUpdatedVideo) {
      try {
        await mutate([GET_OFFER_QUERY_KEY, offer.id], handleVideoOnSubmit(), {
          revalidate: false,
          populateCache: (videoData, offer) => {
            return {
              ...offer,
              videoData,
            }
          },
        })
      } catch (error) {
        snackBar.error(
          getHumanReadableApiError(
            error,
            'Une erreur est survenue lors de l’enregistrement de votre vidéo'
          )
        )

        return false
      }
    }

    if (mode === OFFER_WIZARD_MODE.EDITION) {
      hasSavedOfferRef.current = true
    }

    return true
  }

  const afterSubmitPath = () =>
    getAfterSubmitPath({
      offerId: offer.id,
      mode,
      isOnboarding,
      followingStep: INDIVIDUAL_OFFER_WIZARD_STEP_IDS.TARIFS,
    })
  const afterSubmitState = () =>
    hasSavedOfferRef.current
      ? { successMessage: 'Votre offre a bien été modifiée.' }
      : undefined
  const { navigationGuardedSubmitHandler, navigationGuardDialog } =
    useFormNavigationGuard({
      afterSubmitPath,
      afterSubmitState,
      form,
      isExternallyDirty: isFormDirty,
      onSubmit,
    })

  const logOnImageDropOrSelected = () => {
    logEvent(Events.DRAG_OR_SELECTED_IMAGE, {
      imageType: UploaderModeEnum.OFFER,
      imageCreationStage: 'add image',
    })
  }

  const handleImageAdded = async (file: File) => {
    const { image, error } = await validateImage(file)
    setImageError(error)

    if (error) {
      uploadZoneRef.current?.focus({ preventScroll: true })
      return
    }

    logOnImageDropOrSelected()
    setDraftImage(image)
    setIsModalImageOpen(true)
  }

  const onImageUploadHandler = async (
    values: OnImageUploadArgs,
    successMessage: string
  ) => {
    setIsModalImageOpen(false)
    setDraftImage(values.imageFile)
    setDraftCredit(values.credit ?? '')
    setDraftAlternativeText(values.alternativeText ?? '')
    try {
      await Promise.resolve(onImageUpload(values))
      snackBar.success(successMessage, editButtonId)
    } catch {
      snackBar.error(
        "Une erreur est survenue lors de l'importation de votre image",
        uploadZoneId
      )
    }
  }

  const onImageDeleteHandler = () => {
    if (offer.isHeadlineOffer && !isDeleteImageOpen) {
      setIsDeleteImageOpen(true)
      return
    }
    setIsDeleteImageOpen(false)
    setIsModalImageOpen(false)
    setDraftImage(undefined)
    setDraftCredit(undefined)
    onImageDelete()
    snackBar.success('L’image a bien été supprimée', uploadZoneId)
  }

  return (
    <>
      <FormProvider {...form}>
        <form onSubmit={navigationGuardedSubmitHandler}>
          <FormLayout>
            {isOfferProductBasedButNotSynchronized(offer) && <ProductBanner />}
            <FormLayout.Section title="Illustrez votre offre">
              <FormLayout.Row className={styles['media-rows']}>
                <FormLayout.Row className={styles['media-cell']}>
                  {hasImage ? (
                    <div className={styles['image']}>
                      <SafeImage
                        alt={alternativeText || 'Prévisualisation de l’image'}
                        testId="image-preview"
                        className={styles['image-preview']}
                        src={imageUrl}
                        placeholder={
                          <ImagePlaceholder
                            className={styles['image-placeholder']}
                          />
                        }
                        credit={draftCredit}
                      />
                      {!isImageReadOnly && (
                        <div className={styles['image-actions']}>
                          <Button
                            ref={editButtonRef}
                            onClick={() => setIsModalImageOpen(true)}
                            variant={ButtonVariant.SECONDARY}
                            color={ButtonColor.NEUTRAL}
                            size={ButtonSize.SMALL}
                            aria-label="Modifier l’image"
                            icon={fullEditIcon}
                            label="Modifier"
                            id={editButtonId}
                          />
                          <Button
                            onClick={onImageDeleteHandler}
                            variant={ButtonVariant.SECONDARY}
                            color={ButtonColor.NEUTRAL}
                            size={ButtonSize.SMALL}
                            icon={fullTrashIcon}
                            label="Supprimer"
                          />
                        </div>
                      )}
                    </div>
                  ) : (
                    <UploadZone
                      key={uploadZoneKey}
                      ref={uploadZoneRef}
                      id={uploadZoneId}
                      label="Ajoutez une image"
                      labelVariant="title3"
                      icon={strokePictureIcon}
                      accept={ALLOWED_IMAGE_TYPES_TO_EXTENSIONS}
                      maxSize={MAX_FILE_SIZE}
                      conditionsText={IMAGE_CONDITIONS_TEXT}
                      maxFiles={1}
                      disabled={isImageReadOnly}
                      error={imageError}
                      onFilesAdded={([file]) => void handleImageAdded(file)}
                    />
                  )}
                  <ModalImageUpsertOrEdit
                    mode={UploaderModeEnum.OFFER}
                    onImageUpload={onImageUploadHandler}
                    onImageDelete={onImageDeleteHandler}
                    initialValues={{
                      ...initialValues,
                      draftImage,
                      credit: draftCredit,
                      alternativeText: draftAlternativeText,
                    }}
                    refToFocusOnClose={hasImage ? editButtonRef : uploadZoneRef}
                    onOpenChange={(open) => {
                      if (!open) {
                        setUploadZoneKey((prev) => prev + 1)
                      }
                      setIsModalImageOpen(open)
                    }}
                    open={isModalImageOpen}
                  />
                  <SimpleModal
                    title="Votre offre ne sera plus à la une"
                    iconPath={strokeWarningIcon}
                    isOpen={isDeleteImageOpen}
                    onClose={() => setIsDeleteImageOpen(false)}
                    actionButtons={[
                      <Button
                        onClick={() => setIsDeleteImageOpen(false)}
                        variant={ButtonVariant.SECONDARY}
                        color={ButtonColor.NEUTRAL}
                        label="Annuler"
                        key="cancel"
                      />,
                      <Button
                        onClick={onImageDeleteHandler}
                        color={ButtonColor.DANGER}
                        label="Supprimer l'image"
                        key="confirm"
                      />,
                    ]}
                  >
                    <p>
                      Sans image d'illustration, cette offre ne pourra plus être
                      mise à la une de votre catalogue.
                    </p>
                    <p>Souhaitez-vous réellement supprimer cette image ?</p>
                  </SimpleModal>
                </FormLayout.Row>
                <FormLayout.Row className={styles['media-cell']}>
                  <div className={styles['media-wrapper']}>
                    <h3 className={styles['media-title']}>Ajoutez une vidéo</h3>
                    <VideoUploader uploadTipsId={tipsVideoUploaderId} />
                    {!videoData?.videoThumbnailUrl && (
                      <div id={tipsVideoUploaderId}>
                        <VideoUploaderTips />
                      </div>
                    )}
                  </div>
                </FormLayout.Row>
              </FormLayout.Row>
            </FormLayout.Section>
          </FormLayout>
          <ActionBar
            isEmbedded
            onClickPrevious={handlePreviousStep}
            step={INDIVIDUAL_OFFER_WIZARD_STEP_IDS.MEDIA}
            isDisabled={
              form.formState.isSubmitting ||
              isOfferDisabled(offer) ||
              (!isFormDirty && mode !== OFFER_WIZARD_MODE.CREATION)
            }
          />
        </form>
      </FormProvider>

      {navigationGuardDialog}
    </>
  )
}
