import { FormikProvider } from 'formik'
import React, { useState } from 'react'

import FormLayout from 'components/FormLayout'
import { OFFER_WIZARD_STEP_IDS } from 'components/OfferIndividualBreadcrumb'
import { RouteLeavingGuardOfferIndividual } from 'components/RouteLeavingGuardOfferIndividual'
import { OFFER_WIZARD_MODE } from 'core/Offers'
import { IOfferIndividual } from 'core/Offers/types'
import { getOfferIndividualUrl } from 'core/Offers/utils/getOfferIndividualUrl'
import { useNavigate, useOfferWizardMode } from 'hooks'

import { ActionBar } from '../ActionBar'

import { usePriceCategoriesForm } from './form/useForm'
import { PriceCategoriesForm } from './PriceCategoriesForm'

export interface IPriceCategories {
  offer: IOfferIndividual
}

const PriceCategories = ({ offer }: IPriceCategories): JSX.Element => {
  const [
    isSubmittingFromRouteLeavingGuard,
    setIsSubmittingFromRouteLeavingGuard,
  ] = useState<boolean>(false)
  const [isClickingFromActionBar, setIsClickingFromActionBar] =
    useState<boolean>(false)
  const navigate = useNavigate()
  const mode = useOfferWizardMode()
  const [isClickingDraft, setIsClickingDraft] = useState<boolean>(false)
  const afterSubmitCallback = () => {
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

  const formik = usePriceCategoriesForm(offer, afterSubmitCallback)

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
    () => {
      setIsClickingFromActionBar(true)
      if (saveDraft) {
        // pass value to submit function
        setIsClickingDraft(true)
      }

      const isFormEmpty = formik.values === formik.initialValues

      // When saving draft with an empty form
      // TODO : we display a success notification even if nothing is done
      /* istanbul ignore next: DEBT, TO FIX when we have notification*/
      if (saveDraft && isFormEmpty) {
        setIsClickingDraft(true)
        setIsClickingFromActionBar(false)
        return
      }

      /* istanbul ignore next: DEBT, TO FIX */
      if (Object.keys(formik.errors).length !== 0) {
        setIsClickingFromActionBar(false)
      }

      if (saveDraft) {
        formik.handleSubmit()
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
