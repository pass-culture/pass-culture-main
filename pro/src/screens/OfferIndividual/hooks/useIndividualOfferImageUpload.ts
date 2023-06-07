import { useCallback, useState } from 'react'

import { IOnImageUploadArgs } from 'components/ImageUploader/ButtonImageEdit/ModalImageEdit/ModalImageEdit'
import { OFFER_WIZARD_STEP_IDS } from 'components/OfferIndividualBreadcrumb'
import { useOfferIndividualContext } from 'context/OfferIndividualContext'
import {
  Events,
  OFFER_FORM_NAVIGATION_MEDIUM,
} from 'core/FirebaseEvents/constants'
import { OFFER_WIZARD_MODE } from 'core/Offers'
import { createThumbnailAdapter } from 'core/Offers/adapters/createThumbnailAdapter'
import { deleteThumbnailAdapter } from 'core/Offers/adapters/deleteThumbnailAdapter'
import { IOfferIndividualImage } from 'core/Offers/types'
import { SENT_DATA_ERROR_MESSAGE } from 'core/shared'
import { useOfferWizardMode } from 'hooks'
import useAnalytics from 'hooks/useAnalytics'
import useNotification from 'hooks/useNotification'

import { imageFileToDataUrl } from '../Informations/utils/files'

export const useIndividualOfferImageUpload = () => {
  const notify = useNotification()
  const { logEvent } = useAnalytics()
  const mode = useOfferWizardMode()
  const { offerId, offer, setOffer } = useOfferIndividualContext()

  const [imageOfferCreationArgs, setImageOfferCreationArgs] = useState<
    IOnImageUploadArgs | undefined
  >(undefined)
  const [imageOffer, setImageOffer] = useState<
    IOfferIndividualImage | undefined
  >(offer && offer.image ? offer.image : undefined)

  const handleImageOnSubmit = useCallback(
    async (
      imageOfferId: number,
      imageEditionCreationArgs?: IOnImageUploadArgs
    ) => {
      // Param is passed through state when the offer is not created yet and through param
      // in edition, which is not ideal. We should only have one flow here
      const creationArgs = imageOfferCreationArgs ?? imageEditionCreationArgs
      if (creationArgs === undefined) {
        return
      }
      const { imageFile, credit, cropParams } = creationArgs

      const response = await createThumbnailAdapter({
        offerId: imageOfferId,
        credit,
        imageFile,
        cropParams,
      })

      if (!response.isOk) {
        return Promise.reject()
      }

      setImageOffer({
        originalUrl: response.payload.url,
        url: response.payload.url,
        credit: response.payload.credit,
      })
      if (setOffer && offer) {
        setOffer({
          ...offer,
          image: {
            originalUrl: response.payload.url,
            url: response.payload.url,
            credit: response.payload.credit,
          },
        })
      }
      return Promise.resolve()
    },
    [imageOfferCreationArgs]
  )

  const onImageUpload = async ({
    imageFile,
    imageCroppedDataUrl,
    credit,
    cropParams,
  }: IOnImageUploadArgs) => {
    const creationArgs = {
      imageFile,
      credit,
      cropParams,
    }
    if (offerId === null) {
      setImageOfferCreationArgs(creationArgs)
      imageFileToDataUrl(imageFile, imageUrl => {
        setImageOffer({
          originalUrl: imageUrl,
          url: imageCroppedDataUrl || imageUrl,
          credit,
          cropParams: cropParams
            ? {
                xCropPercent: cropParams.x,
                yCropPercent: cropParams.y,
                heightCropPercent: cropParams.height,
                widthCropPercent: cropParams.width,
              }
            : undefined,
        })
      })
      logEvent?.(Events.CLICKED_OFFER_FORM_NAVIGATION, {
        from: OFFER_WIZARD_STEP_IDS.INFORMATIONS,
        to: OFFER_WIZARD_STEP_IDS.INFORMATIONS,
        used: OFFER_FORM_NAVIGATION_MEDIUM.IMAGE_CREATION,
        isEdition: mode !== OFFER_WIZARD_MODE.CREATION,
        isDraft: mode !== OFFER_WIZARD_MODE.EDITION,
        offerId: undefined,
      })
    } else {
      try {
        await handleImageOnSubmit(offerId, creationArgs)
        logEvent?.(Events.CLICKED_OFFER_FORM_NAVIGATION, {
          from: OFFER_WIZARD_STEP_IDS.INFORMATIONS,
          to: OFFER_WIZARD_STEP_IDS.INFORMATIONS,
          used: OFFER_FORM_NAVIGATION_MEDIUM.IMAGE_CREATION,
          isEdition: mode !== OFFER_WIZARD_MODE.CREATION,
          isDraft: mode !== OFFER_WIZARD_MODE.EDITION,
          offerId: offerId,
        })
      } catch {
        notify.error(SENT_DATA_ERROR_MESSAGE)
      }
    }
  }

  const onImageDelete = async () => {
    /* istanbul ignore next: DEBT, TO FIX */
    if (!offerId) {
      /* istanbul ignore next: DEBT, TO FIX */
      setImageOffer(undefined)
      /* istanbul ignore next: DEBT, TO FIX */
      setImageOfferCreationArgs(undefined)
      logEvent?.(Events.CLICKED_OFFER_FORM_NAVIGATION, {
        from: OFFER_WIZARD_STEP_IDS.INFORMATIONS,
        to: OFFER_WIZARD_STEP_IDS.INFORMATIONS,
        used: OFFER_FORM_NAVIGATION_MEDIUM.IMAGE_DELETE,
        isEdition: mode !== OFFER_WIZARD_MODE.CREATION,
        isDraft: mode !== OFFER_WIZARD_MODE.EDITION,
        offerId: undefined,
      })
    } else {
      const response = await deleteThumbnailAdapter(offerId)
      if (response.isOk) {
        logEvent?.(Events.CLICKED_OFFER_FORM_NAVIGATION, {
          from: OFFER_WIZARD_STEP_IDS.INFORMATIONS,
          to: OFFER_WIZARD_STEP_IDS.INFORMATIONS,
          used: OFFER_FORM_NAVIGATION_MEDIUM.IMAGE_DELETE,
          isEdition: mode !== OFFER_WIZARD_MODE.CREATION,
          isDraft: mode !== OFFER_WIZARD_MODE.EDITION,
          offerId: offerId,
        })
        setImageOffer(undefined)
      } else {
        notify.error(response.message)
      }
    }
  }

  return {
    imageOffer,
    onImageUpload,
    onImageDelete,
    handleImageOnSubmit,
  }
}
