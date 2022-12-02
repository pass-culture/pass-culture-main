import { FormikProvider, useFormik } from 'formik'
import React, { useState } from 'react'
import { useLocation } from 'react-router'

import FormLayout from 'components/FormLayout'
import { IOnImageUploadArgs } from 'components/ImageUploader/ButtonImageEdit/ModalImageEdit/ModalImageEdit'
import {
  IOfferIndividualFormValues,
  OfferIndividualForm,
  validationSchema,
} from 'components/OfferIndividualForm'
import { OFFER_WIZARD_STEP_IDS } from 'components/OfferIndividualStepper'
import { RouteLeavingGuardOfferIndividual } from 'components/RouteLeavingGuardOfferIndividual'
import { useOfferIndividualContext } from 'context/OfferIndividualContext'
import {
  Events,
  OFFER_FORM_NAVIGATION_MEDIUM,
  OFFER_FORM_NAVIGATION_OUT,
} from 'core/FirebaseEvents/constants'
import { CATEGORY_STATUS, OFFER_WIZARD_MODE } from 'core/Offers'
import {
  createIndividualOffer,
  getOfferIndividualAdapter,
  updateIndividualOffer,
} from 'core/Offers/adapters'
import { createThumbnailAdapter } from 'core/Offers/adapters/createThumbnailAdapter'
import { deleteThumbnailAdapter } from 'core/Offers/adapters/deleteThumbnailAdapter'
import { IOfferIndividualImage } from 'core/Offers/types'
import { getOfferIndividualUrl } from 'core/Offers/utils/getOfferIndividualUrl'
import { FORM_ERROR_MESSAGE, SENT_DATA_ERROR_MESSAGE } from 'core/shared'
import { TOfferIndividualVenue } from 'core/Venue/types'
import { useNavigate, useOfferWizardMode } from 'hooks'
import useAnalytics from 'hooks/useAnalytics'
import useNotification from 'hooks/useNotification'

import { ActionBar } from '../ActionBar'
import { logTo } from '../utils/logTo'

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
  const location = useLocation()
  const mode = useOfferWizardMode()
  const { logEvent } = useAnalytics()
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
  const [
    isSubmittingFromRouteLeavingGuard,
    setIsSubmittingFromRouteLeavingGuard,
  ] = useState<boolean>(false)
  const [isClickingFromActionBar, setIsClickingFromActionBar] =
    useState<boolean>(false)

  const handleNextStep =
    ({ saveDraft = false } = {}) =>
    () => {
      setIsClickingFromActionBar(true)
      setIsSubmittingDraft(saveDraft)
      if (Object.keys(formik.errors).length !== 0) {
        /* istanbul ignore next: DEBT, TO FIX */
        setIsClickingFromActionBar(false)
        if (saveDraft) {
          notify.error(
            'Des informations sont nécessaires pour sauvegarder le brouillon'
          )
        } else {
          notify.error(FORM_ERROR_MESSAGE)
        }
      }
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
      logEvent?.(Events.CLICKED_OFFER_FORM_NAVIGATION, {
        from: OFFER_WIZARD_STEP_IDS.INFORMATIONS,
        to: OFFER_WIZARD_STEP_IDS.INFORMATIONS,
        used: OFFER_FORM_NAVIGATION_MEDIUM.IMAGE_DELETE,
        isEdition: mode !== OFFER_WIZARD_MODE.CREATION,
        isDraft: mode !== OFFER_WIZARD_MODE.EDITION,
        offerId: undefined,
      })
    } else {
      submitImage({
        imageOfferId: offerId,
        imageFile,
        credit,
        cropParams,
      })
        .then(() => {
          notify.success('Brouillon sauvegardé dans la liste des offres')
          logEvent?.(Events.CLICKED_OFFER_FORM_NAVIGATION, {
            from: OFFER_WIZARD_STEP_IDS.INFORMATIONS,
            to: OFFER_WIZARD_STEP_IDS.INFORMATIONS,
            used: OFFER_FORM_NAVIGATION_MEDIUM.IMAGE_DELETE,
            isEdition: mode !== OFFER_WIZARD_MODE.CREATION,
            isDraft: mode !== OFFER_WIZARD_MODE.EDITION,
            offerId: offerId,
          })
        })
        .catch(() => {
          notify.error(SENT_DATA_ERROR_MESSAGE)
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
      logEvent?.(Events.CLICKED_OFFER_FORM_NAVIGATION, {
        from: OFFER_WIZARD_STEP_IDS.INFORMATIONS,
        to: OFFER_WIZARD_STEP_IDS.INFORMATIONS,
        used: OFFER_FORM_NAVIGATION_MEDIUM.IMAGE_DELETE,
        isEdition: mode !== OFFER_WIZARD_MODE.CREATION,
        isDraft: mode !== OFFER_WIZARD_MODE.EDITION,
        offerId: undefined,
      })
    } else {
      const response = await deleteThumbnailAdapter({ offerId })
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
    Promise.resolve()
  }

  const onSubmitOffer = async (formValues: IOfferIndividualFormValues) => {
    const { isOk, payload } = !offer
      ? await createIndividualOffer(formValues)
      : await updateIndividualOffer({ offer, formValues })

    const nextStep =
      mode === OFFER_WIZARD_MODE.EDITION
        ? OFFER_WIZARD_STEP_IDS.SUMMARY
        : isSubmittingDraft
        ? OFFER_WIZARD_STEP_IDS.INFORMATIONS
        : OFFER_WIZARD_STEP_IDS.STOCKS

    if (isOk) {
      const receivedOfferId = payload.id
      // FIXME: find a way to test FileReader
      /* istanbul ignore next: DEBT, TO FIX */
      imageOfferCreationArgs &&
        (await submitImage({
          ...imageOfferCreationArgs,
          imageOfferId: receivedOfferId,
        }))
      const response = await getOfferIndividualAdapter(payload.id)
      // This do not trigger a visal change, it's complicated to test
      /* istanbul ignore next: DEBT, TO FIX */
      if (response.isOk) {
        setOffer && setOffer(response.payload)
      }
      notify.success(
        mode === OFFER_WIZARD_MODE.EDITION
          ? 'Vos modifications ont bien été enregistrées'
          : 'Brouillon sauvegardé dans la liste des offres'
      )
      if (!isSubmittingFromRouteLeavingGuard) {
        // replace url to fix back button
        navigate(
          getOfferIndividualUrl({
            step: OFFER_WIZARD_STEP_IDS.INFORMATIONS,
            offerId: receivedOfferId,
            mode,
          }),
          { replace: true }
        )

        navigate(
          getOfferIndividualUrl({
            offerId: receivedOfferId,
            step: nextStep,
            mode,
          })
        )
        logEvent?.(Events.CLICKED_OFFER_FORM_NAVIGATION, {
          from: OFFER_WIZARD_STEP_IDS.INFORMATIONS,
          to: isSubmittingFromRouteLeavingGuard ? location.pathname : nextStep,
          used: isSubmittingDraft
            ? OFFER_FORM_NAVIGATION_MEDIUM.DRAFT_BUTTONS
            : OFFER_FORM_NAVIGATION_MEDIUM.STICKY_BUTTONS,
          isEdition: mode !== OFFER_WIZARD_MODE.CREATION,
          isDraft: mode !== OFFER_WIZARD_MODE.EDITION,
          offerId: receivedOfferId,
        })
      }
    } else {
      formik.setErrors(payload.errors)
    }
    setIsClickingFromActionBar(false)
  }

  const formik = useFormik({
    initialValues,
    onSubmit: onSubmitOffer,
    validationSchema,
    // enableReinitialize is needed to reset dirty after submit (and not block after saving a draft)
    enableReinitialize: true,
  })

  const initialVenue: TOfferIndividualVenue | undefined = venueList.find(
    venue => venue.id === initialValues.venueId
  )

  const [filteredCategories, filteredSubCategories] = filterCategories(
    categories,
    subCategories,
    initialVenue === undefined
      ? CATEGORY_STATUS.ONLINE_OR_OFFLINE
      : initialVenue.isVirtual
      ? CATEGORY_STATUS.ONLINE
      : CATEGORY_STATUS.OFFLINE
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
            isDisabled={formik.isSubmitting}
            offerId={offer?.id}
          />
        </form>
      </FormLayout>
      {formik.dirty && !isClickingFromActionBar && (
        <RouteLeavingGuardOfferIndividual
          saveForm={formik.handleSubmit}
          setIsSubmittingFromRouteLeavingGuard={
            setIsSubmittingFromRouteLeavingGuard
          }
          mode={mode}
          isFormValid={formik.isValid}
          tracking={nextLocation =>
            logEvent?.(Events.CLICKED_OFFER_FORM_NAVIGATION, {
              from: OFFER_WIZARD_STEP_IDS.INFORMATIONS,
              to: logTo(nextLocation),
              used: OFFER_FORM_NAVIGATION_OUT.ROUTE_LEAVING_GUARD,
              isEdition: mode !== OFFER_WIZARD_MODE.CREATION,
              isDraft: mode !== OFFER_WIZARD_MODE.EDITION,
              // FIX ME: it is always undefined at first creation (not sure it is possible)
              offerId: offer?.id,
            })
          }
          hasOfferBeenCreated={!!offer?.id}
        />
      )}
    </FormikProvider>
  )
}

export default Informations
