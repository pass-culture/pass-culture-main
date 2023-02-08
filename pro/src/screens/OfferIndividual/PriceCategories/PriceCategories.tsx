import { FormikProvider } from 'formik'
import React, { useState } from 'react'

import FormLayout from 'components/FormLayout'
import { OFFER_WIZARD_STEP_IDS } from 'components/OfferIndividualBreadcrumb'
import { RouteLeavingGuardOfferIndividual } from 'components/RouteLeavingGuardOfferIndividual'
import { useOfferIndividualContext } from 'context/OfferIndividualContext'
import {
  Events,
  OFFER_FORM_NAVIGATION_MEDIUM,
  OFFER_FORM_NAVIGATION_OUT,
} from 'core/FirebaseEvents/constants'
import { OFFER_WIZARD_MODE } from 'core/Offers'
import { IOfferIndividual } from 'core/Offers/types'
import { getOfferIndividualUrl } from 'core/Offers/utils/getOfferIndividualUrl'
import { useNavigate, useOfferWizardMode } from 'hooks'
import useAnalytics from 'hooks/useAnalytics'
import useNotification from 'hooks/useNotification'

import { ActionBar } from '../ActionBar'
import { getSuccessMessage } from '../utils'
import { logTo } from '../utils/logTo'

import { usePriceCategoriesForm } from './form/useForm'
import { PriceCategoriesForm } from './PriceCategoriesForm'

export interface IPriceCategories {
  offer: IOfferIndividual
}

const PriceCategories = ({ offer }: IPriceCategories): JSX.Element => {
  const { setOffer } = useOfferIndividualContext()
  const { logEvent } = useAnalytics()
  const [
    isSubmittingFromRouteLeavingGuard,
    setIsSubmittingFromRouteLeavingGuard,
  ] = useState<boolean>(false)
  const [isClickingFromActionBar, setIsClickingFromActionBar] =
    useState<boolean>(false)
  const navigate = useNavigate()
  const mode = useOfferWizardMode()
  const [isClickingDraft, setIsClickingDraft] = useState<boolean>(false)
  const notify = useNotification()

  const afterSubmitCallback = () => {
    notify.success(getSuccessMessage(mode))
    if (isSubmittingFromRouteLeavingGuard) {
      return
    }
    const afterSubmitUrl = getOfferIndividualUrl({
      offerId: offer.id,
      step:
        mode === OFFER_WIZARD_MODE.EDITION
          ? OFFER_WIZARD_STEP_IDS.SUMMARY
          : isClickingDraft
          ? OFFER_WIZARD_STEP_IDS.TARIFS
          : OFFER_WIZARD_STEP_IDS.STOCKS,
      mode,
    })
    logEvent?.(Events.CLICKED_OFFER_FORM_NAVIGATION, {
      from: OFFER_WIZARD_STEP_IDS.TARIFS,
      to: isClickingDraft
        ? OFFER_WIZARD_STEP_IDS.TARIFS
        : mode === OFFER_WIZARD_MODE.EDITION
        ? OFFER_WIZARD_STEP_IDS.SUMMARY
        : OFFER_WIZARD_STEP_IDS.STOCKS,
      used: isClickingDraft
        ? OFFER_FORM_NAVIGATION_MEDIUM.DRAFT_BUTTONS
        : OFFER_FORM_NAVIGATION_MEDIUM.STICKY_BUTTONS,
      isEdition: mode !== OFFER_WIZARD_MODE.CREATION,
      isDraft: mode !== OFFER_WIZARD_MODE.EDITION,
      offerId: offer.id,
    })
    navigate(afterSubmitUrl)
    setIsClickingDraft(false)
  }

  const formik = usePriceCategoriesForm(
    offer,
    afterSubmitCallback,
    setOffer,
    notify.error
  )

  const handlePreviousStep = () => {
    if (!formik.dirty) {
      logEvent?.(Events.CLICKED_OFFER_FORM_NAVIGATION, {
        from: OFFER_WIZARD_STEP_IDS.TARIFS,
        to: OFFER_WIZARD_STEP_IDS.INFORMATIONS,
        used: OFFER_FORM_NAVIGATION_MEDIUM.STICKY_BUTTONS,
        isEdition: mode !== OFFER_WIZARD_MODE.CREATION,
        isDraft: mode !== OFFER_WIZARD_MODE.EDITION,
        offerId: offer.id,
      })
    }
    navigate(
      getOfferIndividualUrl({
        offerId: offer.id,
        step: OFFER_WIZARD_STEP_IDS.INFORMATIONS,
        mode,
      })
    )
  }

  const handleNextStep =
    ({ saveDraft = false } = {}) =>
    async () => {
      setIsClickingFromActionBar(true)
      if (saveDraft) {
        // pass value to submit function
        setIsClickingDraft(true)
      }

      const isFormEmpty = formik.values === formik.initialValues

      // When saving draft with an empty form
      /* istanbul ignore next: DEBT, TO FIX when we have notification*/
      if ((saveDraft || mode === OFFER_WIZARD_MODE.EDITION) && isFormEmpty) {
        setIsClickingDraft(true)
        setIsClickingFromActionBar(false)
        if (saveDraft) {
          notify.success(getSuccessMessage(OFFER_WIZARD_MODE.DRAFT))
          return
        } else {
          notify.success(getSuccessMessage(OFFER_WIZARD_MODE.EDITION))
          navigate(
            getOfferIndividualUrl({
              offerId: offer.id,
              step: OFFER_WIZARD_STEP_IDS.SUMMARY,
              mode,
            })
          )
        }
      }

      /* istanbul ignore next: DEBT, TO FIX */
      if (Object.keys(formik.errors).length !== 0) {
        setIsClickingFromActionBar(false)
      }

      if (saveDraft) {
        await formik.submitForm()
      }
    }

  return (
    <FormikProvider value={formik}>
      <FormLayout small>
        <form onSubmit={formik.handleSubmit}>
          <PriceCategoriesForm offerId={offer.nonHumanizedId.toString()} />

          <ActionBar
            onClickPrevious={handlePreviousStep}
            onClickNext={handleNextStep()}
            onClickSaveDraft={handleNextStep({ saveDraft: true })}
            step={OFFER_WIZARD_STEP_IDS.TARIFS}
            isDisabled={formik.isSubmitting}
            offerId={offer.id}
          />
        </form>
      </FormLayout>
      <RouteLeavingGuardOfferIndividual
        when={formik.dirty && !isClickingFromActionBar}
        saveForm={formik.submitForm}
        setIsSubmittingFromRouteLeavingGuard={
          setIsSubmittingFromRouteLeavingGuard
        }
        mode={mode}
        isFormValid={formik.isValid}
        hasOfferBeenCreated
        tracking={nextLocation =>
          logEvent?.(Events.CLICKED_OFFER_FORM_NAVIGATION, {
            from: OFFER_WIZARD_STEP_IDS.TARIFS,
            to: logTo(nextLocation),
            used: OFFER_FORM_NAVIGATION_OUT.ROUTE_LEAVING_GUARD,
            isEdition: mode !== OFFER_WIZARD_MODE.CREATION,
            isDraft: mode !== OFFER_WIZARD_MODE.EDITION,
            offerId: offer?.id,
          })
        }
      />
    </FormikProvider>
  )
}

export default PriceCategories
