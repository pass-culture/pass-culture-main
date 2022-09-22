import { FormikProvider, useFormik } from 'formik'
import React, { useState } from 'react'
import { useHistory } from 'react-router-dom'

import { api } from 'apiClient/api'
import { useOfferIndividualContext } from 'context/OfferIndividualContext'
import {
  createIndividualOffer,
  updateIndividualOffer,
} from 'core/Offers/adapters'
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
import { postThumbnail } from 'repository/pcapi/pcapi'

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
  >()
  const imageOfferOriginal = offer && offer.image ? offer.image : undefined

  const handleNextStep = async () => {
    formik.handleSubmit()
  }

  const onSubmitImage = async ({
    imageData,
    credit,
    cropParams,
  }: IOnImageUploadArgs) => {
    if (!offerId) return
    try {
      const response = await postThumbnail(
        offerId,
        credit,
        imageData,
        undefined, // api don't use thumbUrl
        cropParams?.x,
        cropParams?.y,
        cropParams?.height,
        cropParams?.width
      )

      const { url: urlCreated, credit: creditCreated } = response

      setImageOffer({
        url: urlCreated,
        credit: creditCreated,
      })

      return Promise.resolve()
    } catch {
      return Promise.reject()
    }
  }
  const onImageDelete = async () => {
    if (!offerId) return
    try {
      await api.deleteThumbnail(offerId)
      setImageOffer(undefined)

      return Promise.resolve()
    } catch {
      return Promise.reject()
    }
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
    return Promise.resolve()
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
            imageOffer={imageOffer || imageOfferOriginal}
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
