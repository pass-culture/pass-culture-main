import { Form, FormikProvider, useFormik } from 'formik'
import React, { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useSWRConfig } from 'swr'

import { api } from 'apiClient/api'
import { getHumanReadableApiError } from 'apiClient/helpers'
import { GET_OFFER_QUERY_KEY } from 'commons/config/swrQueryKeys'
import { useIndividualOfferContext } from 'commons/context/IndividualOfferContext/IndividualOfferContext'
import { OFFER_WIZARD_MODE } from 'commons/core/Offers/constants'
import { getIndividualOfferUrl } from 'commons/core/Offers/utils/getIndividualOfferUrl'
import { useNotification } from 'commons/hooks/useNotification'
import { useOfferWizardMode } from 'commons/hooks/useOfferWizardMode'
import { getOfferConditionalFields } from 'commons/utils/getOfferConditionalFields'
import { OFFER_WIZARD_STEP_IDS } from 'components/IndividualOfferNavigation/constants'
import { OfferAppPreview } from 'components/OfferAppPreview/OfferAppPreview'
import { RedirectToBankAccountDialog } from 'components/RedirectToBankAccountDialog/RedirectToBankAccountDialog'
import { SummaryAside } from 'components/SummaryLayout/SummaryAside'
import { SummaryContent } from 'components/SummaryLayout/SummaryContent'
import { SummaryLayout } from 'components/SummaryLayout/SummaryLayout'
import phoneStrokeIcon from 'icons/stroke-phone.svg'
import { ActionBar } from 'pages/IndividualOffer/components/ActionBar/ActionBar'
import { ButtonVariant } from 'ui-kit/Button/types'
import { Callout } from 'ui-kit/Callout/Callout'
import { SvgIcon } from 'ui-kit/SvgIcon/SvgIcon'

import { serializeDateTimeToUTCFromLocalDepartment } from '../StocksEventEdition/serializers'

import { DisplayOfferInAppLink } from './DisplayOfferInAppLink/DisplayOfferInAppLink'
import { EventPublicationForm } from './EventPublicationForm/EventPublicationForm'
import { EventPublicationFormValues } from './EventPublicationForm/types'
import { validationSchema } from './EventPublicationForm/validationSchema'
import { OfferSection } from './OfferSection/OfferSection'
import { PriceCategoriesSection } from './PriceCategoriesSection/PriceCategoriesSection'
import { StockSection } from './StockSection/StockSection'
import styles from './SummaryScreen.module.scss'

export const SummaryScreen = () => {
  const [displayRedirectDialog, setDisplayRedirectDialog] = useState(false)
  const notification = useNotification()
  const mode = useOfferWizardMode()
  const { mutate } = useSWRConfig()
  const navigate = useNavigate()
  const { offer, subCategories } = useIndividualOfferContext()
  const showEventPublicationForm = Boolean(offer?.isEvent)

  const onPublish = async (values: EventPublicationFormValues) => {
    // Edition mode offers are already published
    /* istanbul ignore next: DEBT, TO FIX */
    if (mode === OFFER_WIZARD_MODE.EDITION || offer === null) {
      return
    }

    try {
      const offererResponse = await api.getOfferer(
        offer.venue.managingOfferer.id
      )
      const publishIndividualOfferResponse = await api.patchPublishOffer({
        id: offer.id,
        publicationDate:
          values.publicationMode === 'later'
            ? serializeDateTimeToUTCFromLocalDepartment(
                values.publicationDate,
                values.publicationTime,
                offer.venue.departementCode
              )
            : undefined,
      })
      await mutate([GET_OFFER_QUERY_KEY, offer.id])

      const shouldDisplayRedirectDialog =
        publishIndividualOfferResponse.isNonFreeOffer &&
        !offererResponse.hasNonFreeOffer &&
        !offererResponse.hasValidBankAccount &&
        !offererResponse.hasPendingBankAccount

      if (shouldDisplayRedirectDialog) {
        setDisplayRedirectDialog(true)
      } else {
        navigate(offerConfirmationStepUrl)
      }
    } catch (error) {
      notification.error(getHumanReadableApiError(error))
    }
  }

  const formik = useFormik<EventPublicationFormValues>({
    initialValues: {
      publicationMode: 'now',
      publicationDate: '',
      publicationTime: '',
    },
    onSubmit: onPublish,
    validationSchema: showEventPublicationForm ? validationSchema : undefined,
  })

  if (offer === null) {
    return null
  }

  const canBeDuo = subCategories.find(
    (subCategory) => subCategory.id === offer.subcategoryId
  )?.canBeDuo

  const offerConfirmationStepUrl = getIndividualOfferUrl({
    offerId: offer.id,
    step: OFFER_WIZARD_STEP_IDS.CONFIRMATION,
    mode,
  })

  /* istanbul ignore next: DEBT, TO FIX */
  const handlePreviousStep = () => {
    navigate(
      getIndividualOfferUrl({
        offerId: offer.id,
        step: OFFER_WIZARD_STEP_IDS.STOCKS,
        mode,
      })
    )
  }
  const offerSubCategory = subCategories.find(
    (s) => s.id === offer.subcategoryId
  )

  const offerConditionalFields = getOfferConditionalFields({
    offerSubCategory,
    isUserAdmin: false,
    receiveNotificationEmails: true,
    isVenueVirtual: offer.venue.isVirtual,
  })
  const subCategoryConditionalFields = offerSubCategory
    ? offerSubCategory.conditionalFields
    : []
  const conditionalFields = [
    ...subCategoryConditionalFields,
    ...offerConditionalFields,
  ]

  return (
    <FormikProvider value={formik}>
      <Form>
        {mode === OFFER_WIZARD_MODE.CREATION && (
          <div className={styles['offer-preview-banners']}>
            <Callout>
              <strong>Vous y êtes presque !</strong>
              <br />
              Vérifiez les informations ci-dessous avant de publier votre offre.
              {
                <>
                  <br />
                  Si vous souhaitez la publier plus tard, vous pouvez retrouver
                  votre brouillon dans la liste de vos offres.
                </>
              }
            </Callout>

            {showEventPublicationForm && <EventPublicationForm />}
          </div>
        )}
        <SummaryLayout>
          <SummaryContent>
            <OfferSection
              conditionalFields={conditionalFields}
              offer={offer}
              isEventPublicationFormShown={showEventPublicationForm}
            />

            {mode === OFFER_WIZARD_MODE.CREATION && offer.isEvent && (
              <PriceCategoriesSection offer={offer} canBeDuo={canBeDuo} />
            )}

            {mode === OFFER_WIZARD_MODE.CREATION && (
              <StockSection offer={offer} canBeDuo={canBeDuo} />
            )}
          </SummaryContent>

          <SummaryAside>
            <div className={styles['offer-creation-preview-title']}>
              <SvgIcon
                src={phoneStrokeIcon}
                alt=""
                className={styles['icon-info-phone']}
              />
              <h2 className={styles['title']}>Aperçu dans l’app</h2>
            </div>

            <OfferAppPreview offer={offer} />

            {mode === OFFER_WIZARD_MODE.READ_ONLY && (
              <div className={styles['offer-preview-app-link']}>
                <DisplayOfferInAppLink
                  id={offer.id}
                  variant={ButtonVariant.SECONDARY}
                >
                  Visualiser dans l’app
                </DisplayOfferInAppLink>
              </div>
            )}
          </SummaryAside>
        </SummaryLayout>
        <ActionBar
          onClickPrevious={handlePreviousStep}
          step={OFFER_WIZARD_STEP_IDS.SUMMARY}
          isDisabled={
            mode !== OFFER_WIZARD_MODE.CREATION ? false : formik.isSubmitting
          }
        />
        <RedirectToBankAccountDialog
          cancelRedirectUrl={offerConfirmationStepUrl}
          offerId={offer.venue.managingOfferer.id}
          venueId={offer.venue.id}
          isDialogOpen={displayRedirectDialog}
        />
      </Form>
    </FormikProvider>
  )
}
