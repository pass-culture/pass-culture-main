import { FormikProvider, useFormik } from 'formik'
import React, { useState } from 'react'

import FormLayout from 'components/FormLayout'
import { IOnImageUploadArgs } from 'components/ImageUploader/ButtonImageEdit/ModalImageEdit/ModalImageEdit'
import {
  IOfferIndividualFormValues,
  OfferIndividualForm,
  validationSchema,
} from 'components/OfferIndividualForm'
import { OFFER_WIZARD_STEP_IDS } from 'components/OfferIndividualStepper'
import { useOfferIndividualContext } from 'context/OfferIndividualContext'
import { OFFER_WIZARD_MODE } from 'core/Offers'
import {
  createIndividualOffer,
  getOfferIndividualAdapter,
  updateIndividualOffer,
} from 'core/Offers/adapters'
import { createThumbnailAdapter } from 'core/Offers/adapters/createThumbnailAdapter'
import { deleteThumbnailAdapter } from 'core/Offers/adapters/deleteThumbnailAdapter'
import { IOfferIndividualImage } from 'core/Offers/types'
import { getOfferIndividualUrl } from 'core/Offers/utils/getOfferIndividualUrl'
import { TOfferIndividualVenue } from 'core/Venue/types'
import { useNavigate, useOfferWizardMode } from 'hooks'
import useNotification from 'hooks/useNotification'

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
  const navigate = useNavigate()
  const mode = useOfferWizardMode()
  const {
    offerId,
    offer,
    categories,
    subCategories,
    offererNames,
    venueList,
    setOffer,
  } = useOfferIndividualContext()
  const [imageOfferCreationArgs, setImageOfferCreationArgs] = useState<
    IOnImageUploadArgs | undefined
  >(undefined)
  const [imageOffer, setImageOffer] = useState<
    IOfferIndividualImage | undefined
  >(offer && offer.image ? offer.image : undefined)
  const [isSubmittingDraft, setIsSubmittingDraft] = useState<boolean>(false)

  const handleNextStep =
    ({ saveDraft = false } = {}) =>
    () => {
      setIsSubmittingDraft(saveDraft)
      if (Object.keys(formik.errors).length !== 0)
        notify.error(
          'Une ou plusieurs erreurs sont présentes dans le formulaire',
          {
            withStickyActionBar: true,
          }
        )
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
    /* istanbul ignore next: DEBT, TO FIX */
    if (!offerId) {
      /* istanbul ignore next: DEBT, TO FIX */
      setImageOffer(undefined)
      /* istanbul ignore next: DEBT, TO FIX */
      setImageOfferCreationArgs(undefined)
    } else {
      const response = await deleteThumbnailAdapter({ offerId })
      if (response.isOk) {
        setImageOffer(undefined)
      } else {
        notify.error('Une erreur est survenue. Merci de réessayer plus tard.', {
          withStickyActionBar: true,
        })
      }
    }
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
      const response = await getOfferIndividualAdapter(payload.id)
      // This do not trigger a visal change, it's complicated to test
      /* istanbul ignore next: DEBT, TO FIX */
      if (response.isOk) {
        setOffer && setOffer(response.payload)
      }
      notify.success(
        isSubmittingDraft
          ? 'Brouillon sauvegardé dans la liste des offres'
          : 'Vos modifications ont bien été enregistrées'
      )
      navigate(
        getOfferIndividualUrl({
          offerId: payload.id,
          step: OFFER_WIZARD_STEP_IDS.INFORMATIONS,
          mode,
        }),
        { replace: true }
      )
      navigate(
        getOfferIndividualUrl({
          offerId: payload.id,
          step: isSubmittingDraft
            ? OFFER_WIZARD_STEP_IDS.INFORMATIONS
            : OFFER_WIZARD_STEP_IDS.STOCKS,
          mode: isSubmittingDraft ? OFFER_WIZARD_MODE.DRAFT : mode,
        })
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
            onClickNext={handleNextStep()}
            onClickSaveDraft={handleNextStep({ saveDraft: true })}
            step={OFFER_WIZARD_STEP_IDS.INFORMATIONS}
          />
        </form>
      </FormLayout>
    </FormikProvider>
  )
}

export default Informations
