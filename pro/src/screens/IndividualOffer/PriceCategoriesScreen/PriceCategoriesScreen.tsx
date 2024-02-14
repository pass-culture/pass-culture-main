import { FormikProvider, useFormik } from 'formik'
import React, { useState } from 'react'
import { useNavigate } from 'react-router-dom'

import ConfirmDialog from 'components/Dialog/ConfirmDialog'
import { OFFER_WIZARD_STEP_IDS } from 'components/IndividualOfferNavigation/constants'
import { RouteLeavingGuardIndividualOffer } from 'components/RouteLeavingGuardIndividualOffer/RouteLeavingGuardIndividualOffer'
import { useIndividualOfferContext } from 'context/IndividualOfferContext'
import { OFFER_WIZARD_MODE } from 'core/Offers/constants'
import { IndividualOffer } from 'core/Offers/types'
import { isOfferAllocineSynchronized, isOfferDisabled } from 'core/Offers/utils'
import { getIndividualOfferUrl } from 'core/Offers/utils/getIndividualOfferUrl'
import { useOfferWizardMode } from 'hooks'
import useNotification from 'hooks/useNotification'

import ActionBar from '../ActionBar/ActionBar'
import { getSuccessMessage } from '../utils/getSuccessMessage'

import { computeInitialValues } from './form/computeInitialValues'
import { submitToApi } from './form/submitToApi'
import { PriceCategoriesFormValues, PriceCategoryForm } from './form/types'
import { validationSchema } from './form/validationSchema'
import { PriceCategoriesForm } from './PriceCategoriesForm'

export interface PriceCategoriesScreenProps {
  offer: IndividualOffer
}

const hasFieldChange = (
  priceCategories: PriceCategoryForm[],
  initialPriceCategories: Record<string, Partial<PriceCategoryForm>>,
  field: keyof PriceCategoryForm
) =>
  priceCategories.some((priceCategory) => {
    // if no id, it is new and has no stocks
    if (!priceCategory.id) {
      return false
    }
    // have fields which trigger warning been edited ?
    const initialpriceCategory = initialPriceCategories[priceCategory.id]
    return initialpriceCategory[field] !== priceCategory[field]
  })

export const arePriceCategoriesChanged = (
  initialValues: PriceCategoriesFormValues,
  values: PriceCategoriesFormValues
): boolean => {
  const initialPriceCategories: Record<
    string,
    Partial<PriceCategoryForm>
  > = initialValues.priceCategories.reduce(
    (dict: Record<string, Partial<PriceCategoryForm>>, priceCategory) => {
      dict[priceCategory.id || 'new'] = {
        id: priceCategory.id,
        label: priceCategory.label,
        price: priceCategory.price,
      }
      return dict
    },
    {}
  )

  const changedPriceCategories = values.priceCategories.filter(
    (priceCategory) => {
      if (!priceCategory.id) {
        return false
      }
      if (
        priceCategory.price !==
          initialPriceCategories[priceCategory.id].price ||
        priceCategory.label !== initialPriceCategories[priceCategory.id].label
      ) {
        return true
      }
      return false
    }
  )

  return hasFieldChange(changedPriceCategories, initialPriceCategories, 'price')
}

export const PriceCategoriesScreen = ({
  offer,
}: PriceCategoriesScreenProps): JSX.Element => {
  const { subCategories } = useIndividualOfferContext()
  const navigate = useNavigate()
  const mode = useOfferWizardMode()
  const notify = useNotification()
  const [isConfirmationModalOpen, setIsConfirmationModalOpen] =
    useState<boolean>(false)

  const isDisabledBySynchronization =
    Boolean(offer.lastProvider) && !isOfferAllocineSynchronized(offer)
  const isDisabledByStatus = offer.status
    ? isOfferDisabled(offer.status)
    : false
  const isDisabled = isDisabledByStatus || isDisabledBySynchronization
  const canBeDuo = subCategories.find(
    (subCategory) => subCategory.id === offer.subcategoryId
  )?.canBeDuo

  const onSubmit = async (values: PriceCategoriesFormValues) => {
    const nextStepUrl = getIndividualOfferUrl({
      offerId: offer.id,
      step:
        mode === OFFER_WIZARD_MODE.EDITION
          ? OFFER_WIZARD_STEP_IDS.TARIFS
          : OFFER_WIZARD_STEP_IDS.STOCKS,
      mode:
        mode === OFFER_WIZARD_MODE.EDITION ? OFFER_WIZARD_MODE.READ_ONLY : mode,
    })

    // Return when saving in edition with an empty form
    const isFormEmpty = formik.values === formik.initialValues
    if (isFormEmpty && mode === OFFER_WIZARD_MODE.EDITION) {
      navigate(nextStepUrl)
      notify.success(getSuccessMessage(mode))
      return
    }

    // Show popin if necessary
    const showConfirmationModal =
      offer.hasStocks && arePriceCategoriesChanged(formik.initialValues, values)
    setIsConfirmationModalOpen(showConfirmationModal)
    if (!isConfirmationModalOpen && showConfirmationModal) {
      return
    }

    // Submit
    try {
      await submitToApi(values, offer, formik.resetForm)
    } catch (error) {
      if (error instanceof Error) {
        notify.error(error?.message)
      }
      return
    }

    navigate(nextStepUrl)
    if (mode === OFFER_WIZARD_MODE.EDITION) {
      notify.success(getSuccessMessage(mode))
    }
    setIsConfirmationModalOpen(false)
  }

  const initialValues = computeInitialValues(offer)

  const formik = useFormik<PriceCategoriesFormValues>({
    initialValues,
    validationSchema,
    onSubmit,
  })

  const handlePreviousStepOrBackToReadOnly = () => {
    mode === OFFER_WIZARD_MODE.EDITION
      ? navigate(
          getIndividualOfferUrl({
            offerId: offer.id,
            step: OFFER_WIZARD_STEP_IDS.TARIFS,
            mode: OFFER_WIZARD_MODE.READ_ONLY,
          })
        )
      : navigate(
          getIndividualOfferUrl({
            offerId: offer.id,
            step: OFFER_WIZARD_STEP_IDS.INFORMATIONS,
            mode,
          })
        )
  }

  return (
    <FormikProvider value={formik}>
      {isConfirmationModalOpen && (
        <ConfirmDialog
          onCancel={() => setIsConfirmationModalOpen(false)}
          onConfirm={formik.submitForm}
          title="Cette modification de tarif s’appliquera à l’ensemble des dates qui y sont associées."
          confirmText="Confirmer la modification"
          cancelText="Annuler"
        >
          {(offer.bookingsCount ?? 0) > 0 && (
            <>
              Le tarif restera inchangé pour les personnes ayant déjà réservé
              cette offre.
            </>
          )}
        </ConfirmDialog>
      )}

      <form onSubmit={formik.handleSubmit}>
        <PriceCategoriesForm
          offer={offer}
          mode={mode}
          isDisabled={isDisabled}
          canBeDuo={canBeDuo}
        />

        <ActionBar
          onClickPrevious={handlePreviousStepOrBackToReadOnly}
          step={OFFER_WIZARD_STEP_IDS.TARIFS}
          isDisabled={formik.isSubmitting}
          dirtyForm={formik.dirty}
        />
      </form>

      <RouteLeavingGuardIndividualOffer
        when={formik.dirty && !formik.isSubmitting}
      />
    </FormikProvider>
  )
}
