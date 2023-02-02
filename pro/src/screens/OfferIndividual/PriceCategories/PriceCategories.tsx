import { FormikProvider } from 'formik'
import React, { useState } from 'react'

import FormLayout from 'components/FormLayout'
import { OFFER_WIZARD_STEP_IDS } from 'components/OfferIndividualBreadcrumb'
import { RouteLeavingGuardOfferIndividual } from 'components/RouteLeavingGuardOfferIndividual'
import { useOfferIndividualContext } from 'context/OfferIndividualContext'
import { OFFER_WIZARD_MODE } from 'core/Offers'
import { IOfferIndividual } from 'core/Offers/types'
import { getOfferIndividualUrl } from 'core/Offers/utils/getOfferIndividualUrl'
import { useNavigate, useOfferWizardMode } from 'hooks'
import useNotification from 'hooks/useNotification'

import { ActionBar } from '../ActionBar'
import { getSuccessMessage } from '../utils'

import { usePriceCategoriesForm } from './form/useForm'
import { PriceCategoriesForm } from './PriceCategoriesForm'

export interface IPriceCategories {
  offer: IOfferIndividual
}

const PriceCategories = ({ offer }: IPriceCategories): JSX.Element => {
  const { setOffer } = useOfferIndividualContext()
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
    navigate(
      getOfferIndividualUrl({
        offerId: offer.id,
        step:
          mode === OFFER_WIZARD_MODE.EDITION
            ? OFFER_WIZARD_STEP_IDS.SUMMARY
            : isClickingDraft
            ? OFFER_WIZARD_STEP_IDS.TARIFS
            : OFFER_WIZARD_STEP_IDS.STOCKS,
        mode,
      })
    )
    setIsClickingDraft(false)
  }

  const formik = usePriceCategoriesForm(
    offer,
    afterSubmitCallback,
    setOffer,
    notify.error
  )

  const handlePreviousStep = () => {
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
          <PriceCategoriesForm />

          <ActionBar
            onClickPrevious={handlePreviousStep}
            onClickNext={handleNextStep()}
            onClickSaveDraft={handleNextStep({ saveDraft: true })}
            step={OFFER_WIZARD_STEP_IDS.STOCKS}
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
      />
    </FormikProvider>
  )
}

export default PriceCategories
