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
import FormLayout from 'new_components/FormLayout'
import { IOnImageUploadArgs } from 'new_components/ImageUploader/ButtonImageEdit/ModalImageEdit/ModalImageEdit'
import { OfferFormLayout } from 'new_components/OfferFormLayout'
import {
  IOfferIndividualFormValues,
  OfferIndividualForm,
  validationSchema,
} from 'new_components/OfferIndividualForm'
import useIsCreation from 'new_components/OfferIndividualStepper/hooks/useIsCreation'

import { ActionBar } from '../ActionBar'

import { filterCategories } from './utils'

export interface IInformationsProps {
  initialValues: IOfferIndividualFormValues
  readOnlyFields?: string[]
}

const Informations = ({
  initialValues,
  readOnlyFields = [],
}: IInformationsProps): JSX.Element => {
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
  const [imageOffer, setImageOffer] = useState<
    IOfferIndividualImage | undefined
  >(offer && offer.image ? offer.image : undefined)

  const handleNextStep = async () => {
    formik.handleSubmit()
  }

  // In order to test this we need to find a way to mock canvas.
  /* istanbul ignore next */
  const onSubmitImage = async ({
    imageData,
    credit,
    cropParams,
  }: IOnImageUploadArgs) => {
    if (!offerId) return
    const response = await createThumbnailAdapter({
      offerId,
      credit,
      imageData,
      cropParams,
    })
    if (response.isOk) {
      setImageOffer({
        url: response.payload.url,
        credit: response.payload.credit,
      })
      return Promise.resolve()
    }
    return Promise.reject()
  }
  const onImageDelete = async () => {
    if (!offerId) return
    const response = await deleteThumbnailAdapter({ offerId })
    if (response.isOk) {
      setImageOffer(undefined)
      return Promise.resolve()
    }
    return Promise.reject()
  }

  const onSubmitOffer = async (formValues: IOfferIndividualFormValues) => {
    const { isOk, payload } =
      offerId === null
        ? await createIndividualOffer(formValues)
        : await updateIndividualOffer({ offerId, formValues })

    if (isOk) {
      await reloadOffer()
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
            onImageUpload={onSubmitImage}
            onImageDelete={onImageDelete}
            imageOffer={imageOffer}
          />
          <OfferFormLayout.ActionBar>
            <ActionBar onClickNext={handleNextStep} />
          </OfferFormLayout.ActionBar>
        </form>
      </FormLayout>
    </FormikProvider>
  )
}

export default Informations
