import { FormikProvider, useFormik } from 'formik'
import React, { useState } from 'react'
import { useHistory } from 'react-router-dom'

import { useOfferIndividualContext } from 'context/OfferIndividualContext'
import {
  createIndividualOffer,
  updateIndividualOffer,
} from 'core/Offers/adapters'
import { createThumbnailAdapter } from 'core/Offers/adapters/createThumbnailAdapter'
import { deleteThumbnailAdapter } from 'core/Offers/adapters/deleteThumbnailAdapter'
import { IOfferIndividualImage } from 'core/Offers/types'
import { TOfferIndividualVenue } from 'core/Venue/types'
import useNotification from 'hooks/useNotification'
import FormLayout from 'new_components/FormLayout'
import { IOnImageUploadArgs } from 'new_components/ImageUploader/ButtonImageEdit/ModalImageEdit/ModalImageEdit'
import {
  IOfferIndividualFormValues,
  OfferIndividualForm,
  validationSchema,
} from 'new_components/OfferIndividualForm'
import { OFFER_WIZARD_STEP_IDS } from 'new_components/OfferIndividualStepper'
import useIsCreation from 'new_components/OfferIndividualStepper/hooks/useIsCreation'

import { ActionBar } from '../ActionBar'

import { filterCategories } from './utils'
import { imageFileToDataUrl } from './utils/files'

export interface IInformationsProps {
  initialValues: IOfferIndividualFormValues
  readOnlyFields?: string[]
}

const Informations = ({
  initialValues,
  readOnlyFields = [],
}: IInformationsProps): JSX.Element => {
  const notify = useNotification()
  const history = useHistory()
  const isCreation = useIsCreation()
  const {
    offerId,
    offer,
    categories,
    subCategories,
    offererNames,
    venueList,
    reloadOffer,
  } = useOfferIndividualContext()
  const [imageOfferCreationArgs, setImageOfferCreationArgs] = useState<
    IOnImageUploadArgs | undefined
  >(undefined)
  const [imageOffer, setImageOffer] = useState<
    IOfferIndividualImage | undefined
  >(offer && offer.image ? offer.image : undefined)

  const handleNextStep = () => {
    formik.handleSubmit()
  }

  // FIXME: find a way to test FileReader
  /* istanbul ignore next: DEBT, TO FIX */
  const submitImage = async ({
    imageOfferId,
    imageFile,
    credit,
    cropParams,
  }: IOnImageUploadArgs & { imageOfferId: string }) => {
    const response = await createThumbnailAdapter({
      offerId: imageOfferId,
      credit,
      imageFile,
      cropParams,
    })

    if (response.isOk) {
      setImageOffer({
        originalUrl: response.payload.url,
        url: response.payload.url,
        credit: response.payload.credit,
      })
      return Promise.resolve()
    }
    return Promise.reject()
  }

  // FIXME: find a way to test FileReader
  /* istanbul ignore next: DEBT, TO FIX */
  const onImageUpload = async ({
    imageFile,
    imageCroppedDataUrl,
    credit,
    cropParams,
  }: IOnImageUploadArgs) => {
    if (offerId === null) {
      setImageOfferCreationArgs({
        imageFile,
        credit,
        cropParams,
      })
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
    } else {
      submitImage({
        imageOfferId: offerId,
        imageFile,
        credit,
        cropParams,
      })
        .then(() => {
          notify.success('Vos modifications ont bien été prises en compte', {
            withStickyActionBar: true,
          })
        })
        .catch(() => {
          notify.error(
            'Une erreur est survenue lors de la sauvegarde de vos modifications.\n Merci de réessayer plus tard',
            {
              withStickyActionBar: true,
            }
          )
        })
      return Promise.resolve()
    }
  }

  const onImageDelete = async () => {
    // ImageUploader isn't display when we've no offerId
    /* istanbul ignore next */
    if (!offerId) return Promise.resolve()
    const response = await deleteThumbnailAdapter({ offerId })
    if (response.isOk) {
      setImageOffer(undefined)
    }
    notify.error('Une erreur est survenue. Merci de réessayer plus tard.', {
      withStickyActionBar: true,
    })
    Promise.resolve()
  }

  const onSubmitOffer = async (formValues: IOfferIndividualFormValues) => {
    const { isOk, payload } =
      offerId === null
        ? await createIndividualOffer(formValues)
        : await updateIndividualOffer({ offerId, formValues })

    if (isOk) {
      // FIXME: find a way to test FileReader
      /* istanbul ignore next: DEBT, TO FIX */
      imageOfferCreationArgs &&
        (await submitImage({
          ...imageOfferCreationArgs,
          imageOfferId: payload.id,
        }))
      await reloadOffer()
      notify.success('Vos modifications ont bien été prises en compte')
      history.push(
        isCreation
          ? `/offre/${payload.id}/v3/creation/individuelle/stocks`
          : `/offre/${payload.id}/v3/individuelle/stocks`
      )
    } else {
      formik.setErrors(payload.errors)
    }
  }

  const formik = useFormik({
    initialValues,
    onSubmit: onSubmitOffer,
    validationSchema,
  })

  const initialVenue: TOfferIndividualVenue | undefined = venueList.find(
    venue => venue.id === initialValues.venueId
  )

  const [filteredCategories, filteredSubCategories] = filterCategories(
    categories,
    subCategories,
    initialVenue
  )

  return (
    <FormikProvider value={formik}>
      <FormLayout small>
        <form onSubmit={formik.handleSubmit}>
          <OfferIndividualForm
            offererNames={offererNames}
            venueList={venueList}
            categories={filteredCategories}
            subCategories={filteredSubCategories}
            readOnlyFields={readOnlyFields}
            onImageUpload={onImageUpload}
            onImageDelete={onImageDelete}
            imageOffer={imageOffer}
          />
          <ActionBar
            onClickNext={handleNextStep}
            onClickSaveDraft={() => {}}
            isCreation={isCreation}
            step={OFFER_WIZARD_STEP_IDS.INFORMATIONS}
          />
        </form>
      </FormLayout>
    </FormikProvider>
  )
}

export default Informations
