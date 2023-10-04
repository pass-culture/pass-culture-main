import { FormikProvider, useFormik } from 'formik'
import React, { useState } from 'react'
import { useNavigate } from 'react-router-dom'

import ConfirmDialog from 'components/Dialog/ConfirmDialog'
import { OFFER_WIZARD_STEP_IDS } from 'components/IndividualOfferBreadcrumb/constants'
import { RouteLeavingGuardIndividualOffer } from 'components/RouteLeavingGuardIndividualOffer'
import { useIndividualOfferContext } from 'context/IndividualOfferContext'
import { OFFER_WIZARD_MODE } from 'core/Offers/constants'
import { IndividualOffer, IndividualOfferStock } from 'core/Offers/types'
import { isOfferAllocineSynchronized, isOfferDisabled } from 'core/Offers/utils'
import { getIndividualOfferUrl } from 'core/Offers/utils/getIndividualOfferUrl'
import { useOfferWizardMode } from 'hooks'
import useNotification from 'hooks/useNotification'

import ActionBar from '../ActionBar/ActionBar'
import { getSuccessMessage } from '../utils/getSuccessMessage'

import { computeInitialValues } from './form/computeInitialValues'
import { onSubmit } from './form/onSubmit'
import { PriceCategoriesFormValues, PriceCategoryForm } from './form/types'
import { validationSchema } from './form/validationSchema'
import { PriceCategoriesForm } from './PriceCategoriesForm'

export interface PriceCategoriesScreenProps {
  offer: IndividualOffer
}

export enum POPIN_TYPE {
  PRICE = 'price',
  PRICE_WITH_BOOKING = 'priceWithBooking',
}

const hasFieldChange = (
  priceCategories: PriceCategoryForm[],
  initialPriceCategories: Record<string, Partial<PriceCategoryForm>>,
  stockPriceCategoryIds: (number | null | undefined)[],
  field: keyof PriceCategoryForm
) =>
  priceCategories.some(priceCategory => {
    // if no id, it is new and has no stocks
    if (!priceCategory.id) {
      return false
    }
    // have fields which trigger warning been edited ?
    const initialpriceCategory = initialPriceCategories[priceCategory.id]
    if (initialpriceCategory[field] !== priceCategory[field]) {
      // does it match a stock ?
      return stockPriceCategoryIds.some(
        stockPriceCategoryId => stockPriceCategoryId === priceCategory.id
      )
    } else {
      return false
    }
  })

export const getPopinType = (
  stocks: IndividualOfferStock[],
  initialValues: PriceCategoriesFormValues,
  values: PriceCategoriesFormValues
): POPIN_TYPE | null => {
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
    priceCategory => {
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

  const stockPriceCategoryIds = stocks.map(stock => stock.priceCategoryId)

  const priceCategoryWithStocks = changedPriceCategories.filter(
    priceCategory => {
      if (!priceCategory.id) {
        return false
      }
      return stockPriceCategoryIds.some(
        stockPriceCategoryId => stockPriceCategoryId === priceCategory.id
      )
    }
  )

  // when there is no stock, no need for popin
  if (priceCategoryWithStocks.length === 0) {
    return null
  }

  const priceCategoryWithBookings = priceCategoryWithStocks.filter(
    priceCategory => {
      return stocks.some(stock => {
        if (
          stock.priceCategoryId === priceCategory.id &&
          stock.bookingsQuantity > 0
        ) {
          return true
        }
        return false
      })
    }
  )

  if (priceCategoryWithBookings.length > 0) {
    // if there are bookings we want to know if change is on price or label
    if (
      hasFieldChange(
        changedPriceCategories,
        initialPriceCategories,
        stockPriceCategoryIds,
        'price'
      )
    ) {
      return POPIN_TYPE.PRICE_WITH_BOOKING
    }
  } else if (
    // if there are only stocks with no bookings there is a special popin for price
    hasFieldChange(
      changedPriceCategories,
      initialPriceCategories,
      stockPriceCategoryIds,
      'price'
    )
  ) {
    return POPIN_TYPE.PRICE
  }
  return null
}

export const PriceCategoriesScreen = ({
  offer,
}: PriceCategoriesScreenProps): JSX.Element => {
  const { setOffer, subCategories } = useIndividualOfferContext()
  const [isClickingFromActionBar, setIsClickingFromActionBar] =
    useState<boolean>(false)
  const navigate = useNavigate()
  const mode = useOfferWizardMode()
  const notify = useNotification()
  const [popinType, setPopinType] = useState<POPIN_TYPE | null>(null)

  const isDisabledBySynchronization =
    Boolean(offer.lastProvider) && !isOfferAllocineSynchronized(offer)
  const isDisabledByStatus = offer.status
    ? isOfferDisabled(offer.status)
    : false
  const isDisabled = isDisabledByStatus || isDisabledBySynchronization
  const canBeDuo = subCategories.find(
    subCategory => subCategory.id === offer.subcategoryId
  )?.canBeDuo

  const onSubmitWithCallback = async (values: PriceCategoriesFormValues) => {
    const newPopinType = getPopinType(
      offer.stocks,
      formik.initialValues,
      values
    )
    setPopinType(newPopinType)
    if (newPopinType !== null && popinType === null) {
      return
    }

    try {
      await onSubmit(values, offer, setOffer, formik.resetForm)
      afterSubmitCallback()
      setPopinType(null)
    } catch (error) {
      if (error instanceof Error) {
        notify.error(error?.message)
      }
    }
  }

  const afterSubmitCallback = () => {
    const afterSubmitUrl = getIndividualOfferUrl({
      offerId: offer.id,
      step:
        mode === OFFER_WIZARD_MODE.EDITION
          ? OFFER_WIZARD_STEP_IDS.TARIFS
          : OFFER_WIZARD_STEP_IDS.STOCKS,
      mode:
        mode === OFFER_WIZARD_MODE.EDITION ? OFFER_WIZARD_MODE.READ_ONLY : mode,
    })
    navigate(afterSubmitUrl)
    if (mode === OFFER_WIZARD_MODE.EDITION) {
      notify.success(getSuccessMessage(mode))
    }
  }

  const initialValues = computeInitialValues(offer)

  const formik = useFormik<PriceCategoriesFormValues>({
    initialValues,
    validationSchema,
    onSubmit: onSubmitWithCallback,
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

  const handleNextStep = async () => {
    setIsClickingFromActionBar(true)

    const isFormEmpty = formik.values === formik.initialValues

    // When saving draft with an empty form
    /* istanbul ignore next: DEBT, TO FIX when we have notification*/
    if (mode === OFFER_WIZARD_MODE.EDITION && isFormEmpty) {
      setIsClickingFromActionBar(false)
      navigate(
        getIndividualOfferUrl({
          offerId: offer.id,
          step: OFFER_WIZARD_STEP_IDS.SUMMARY,
          mode:
            mode === OFFER_WIZARD_MODE.EDITION
              ? OFFER_WIZARD_MODE.READ_ONLY
              : mode,
        })
      )
      notify.success(getSuccessMessage(OFFER_WIZARD_MODE.EDITION))
    }

    /* istanbul ignore next: DEBT, TO FIX */
    if (Object.keys(formik.errors).length !== 0) {
      setIsClickingFromActionBar(false)
    }
  }

  return (
    <FormikProvider value={formik}>
      {popinType === POPIN_TYPE.PRICE && (
        <ConfirmDialog
          onCancel={() => setPopinType(null)}
          onConfirm={formik.submitForm}
          title="Cette modification de tarif s’appliquera à l’ensemble des occurrences qui y sont associées."
          confirmText="Confirmer la modification"
          cancelText="Annuler"
        />
      )}

      {popinType === POPIN_TYPE.PRICE_WITH_BOOKING && (
        <ConfirmDialog
          onCancel={() => setPopinType(null)}
          onConfirm={formik.submitForm}
          title="Cette modification de tarif s’appliquera à l’ensemble des occurrences qui y sont associées."
          confirmText="Confirmer la modification"
          cancelText="Annuler"
        >
          Le tarif restera inchangé pour les personnes ayant déjà réservé cette
          offre.
        </ConfirmDialog>
      )}

      <form onSubmit={formik.handleSubmit}>
        <PriceCategoriesForm
          offerId={offer.id}
          mode={mode}
          stocks={offer.stocks}
          setOffer={setOffer}
          isDisabled={isDisabled}
          canBeDuo={canBeDuo}
        />

        <ActionBar
          onClickPrevious={handlePreviousStepOrBackToReadOnly}
          step={OFFER_WIZARD_STEP_IDS.TARIFS}
          isDisabled={formik.isSubmitting}
        />
      </form>

      <RouteLeavingGuardIndividualOffer
        when={formik.dirty && !isClickingFromActionBar}
      />
    </FormikProvider>
  )
}
