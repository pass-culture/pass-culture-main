import cn from 'classnames'
import { FieldArray, useFormikContext } from 'formik'
import type { FieldArrayRenderProps } from 'formik'
import React, { useState } from 'react'

import ConfirmDialog from 'components/Dialog/ConfirmDialog'
import FormLayout from 'components/FormLayout'
import { OFFER_WIZARD_MODE } from 'core/Offers'
import { getOfferIndividualAdapter } from 'core/Offers/adapters'
import { IOfferIndividual, IOfferIndividualStock } from 'core/Offers/types'
import useNotification from 'hooks/useNotification'
import { EuroIcon, PlusCircleIcon, TrashFilledIcon } from 'icons'
import { Button, Checkbox, InfoBox, TextInput } from 'ui-kit'
import { ButtonVariant, IconPositionEnum } from 'ui-kit/Button/types'
import { BaseCheckbox } from 'ui-kit/form/shared'

import deletePriceCategoryAdapter from './adapters/deletePriceCategoryAdapter'
import { computeInitialValues } from './form/computeInitialValues'
import {
  INITIAL_PRICE_CATEGORY,
  PRICE_CATEGORY_LABEL_MAX_LENGTH,
  PRICE_CATEGORY_MAX_LENGTH,
  PRICE_CATEGORY_PRICE_MAX,
  UNIQUE_PRICE,
} from './form/constants'
import { PriceCategoriesFormValues } from './form/types'
import styles from './PriceCategoriesForm.module.scss'

interface IPriceCategoriesForm {
  offerId: string
  humanizedOfferId: string
  stocks: IOfferIndividualStock[]
  mode: OFFER_WIZARD_MODE
  setOffer: ((offer: IOfferIndividual | null) => void) | null
}

export const PriceCategoriesForm = ({
  offerId,
  humanizedOfferId,
  stocks,
  mode,
  setOffer,
}: IPriceCategoriesForm): JSX.Element => {
  const { setFieldValue, handleChange, resetForm, values } =
    useFormikContext<PriceCategoriesFormValues>()
  const notify = useNotification()

  const [showConfirmDeletePriceCategory, setShowConfirmDeletePriceCategory] =
    useState(false)

  const [isFreeCheckboxSelectedArray, setIsFreeCheckboxSelectedArray] =
    useState(
      // initialize an array of length with false or true when it's 0
      values.priceCategories.map(priceCategory => priceCategory.price === 0)
    )

  const onChangeFree =
    (index: number) => (e: React.ChangeEvent<HTMLInputElement>) => {
      if (e.target.checked) {
        setFieldValue(`priceCategories[${index}].price`, 0)
      }

      const newCheckboxArray = [...isFreeCheckboxSelectedArray]
      newCheckboxArray[index] = e.target.checked
      setIsFreeCheckboxSelectedArray(newCheckboxArray)
    }

  const onChangePrice =
    (index: number) => (e: React.ChangeEvent<HTMLInputElement>) => {
      const newCheckboxArray = [...isFreeCheckboxSelectedArray]
      newCheckboxArray[index] = e.target.value === '0'
      setIsFreeCheckboxSelectedArray(newCheckboxArray)
      handleChange(e)
    }

  const onDeletePriceCategory = async (
    index: number,
    arrayHelpers: FieldArrayRenderProps,
    priceCategoryId?: number
  ) => {
    if (priceCategoryId) {
      const shouldDisplayConfirmDeletePriceCategory = stocks.some(
        stock => stock.priceCategoryId === priceCategoryId
      )
      if (
        !showConfirmDeletePriceCategory &&
        shouldDisplayConfirmDeletePriceCategory
      ) {
        setShowConfirmDeletePriceCategory(true)
        return
      } else {
        setShowConfirmDeletePriceCategory(false)
      }
      const { isOk, message } = await deletePriceCategoryAdapter({
        offerId,
        priceCategoryId: priceCategoryId.toString(),
      })
      if (isOk) {
        arrayHelpers.remove(index)
        const response = await getOfferIndividualAdapter(humanizedOfferId)
        if (response.isOk) {
          const updatedOffer = response.payload
          setOffer && setOffer(updatedOffer)
          resetForm({
            values: computeInitialValues(updatedOffer),
          })
        }
        notify.success(message)
      } else {
        notify.error(message)
      }
    } else {
      arrayHelpers.remove(index)
    }
    if (values.priceCategories.length === 2) {
      setFieldValue(`priceCategories[0].label`, UNIQUE_PRICE)
    }
  }

  return (
    <>
      <FormLayout.MandatoryInfo />
      <FieldArray
        name="priceCategories"
        render={arrayHelpers => (
          <FormLayout.Section title="Tarifs">
            {values.priceCategories.map((priceCategory, index) => (
              <FormLayout.Row key={index} inline>
                {showConfirmDeletePriceCategory && index === 0 && (
                  <ConfirmDialog
                    onCancel={() => setShowConfirmDeletePriceCategory(false)}
                    onConfirm={() =>
                      onDeletePriceCategory(
                        index,
                        arrayHelpers,
                        values.priceCategories[index].id
                      )
                    }
                    title="En supprimant ce tarif vous allez aussi supprimer l’ensemble des occurrences qui lui sont associées."
                    confirmText="Confirmer la supression"
                    cancelText="Annuler"
                  />
                )}
                <TextInput
                  smallLabel
                  name={`priceCategories[${index}].label`}
                  label="Intitulé du tarif"
                  placeholder="Ex : catégorie 1, orchestre..."
                  maxLength={PRICE_CATEGORY_LABEL_MAX_LENGTH}
                  countCharacters
                  className={styles['label-input']}
                  disabled={values.priceCategories.length <= 1}
                  isLabelHidden={index !== 0}
                />

                <TextInput
                  smallLabel
                  name={`priceCategories[${index}].price`}
                  label="Tarif par personne"
                  placeholder="Ex : 25€"
                  type="number"
                  step="0.01"
                  max={PRICE_CATEGORY_PRICE_MAX}
                  rightIcon={() => <EuroIcon />}
                  className={styles['price-input']}
                  onChange={onChangePrice(index)}
                  isLabelHidden={index !== 0}
                />

                <div
                  className={cn(styles['form-row-actions'], {
                    [styles['first-row']]: index === 0,
                  })}
                >
                  <BaseCheckbox
                    label="Gratuit"
                    checked={isFreeCheckboxSelectedArray[index]}
                    name={`priceCategories[${index}].free`}
                    onChange={onChangeFree(index)}
                  />
                  {mode !== OFFER_WIZARD_MODE.EDITION && (
                    <Button
                      variant={ButtonVariant.TERNARY}
                      Icon={TrashFilledIcon}
                      iconPosition={IconPositionEnum.CENTER}
                      disabled={values.priceCategories.length <= 1}
                      onClick={() =>
                        onDeletePriceCategory(
                          index,
                          arrayHelpers,
                          values.priceCategories[index].id
                        )
                      }
                      hasTooltip
                    >
                      Supprimer le tarif
                    </Button>
                  )}
                </div>
              </FormLayout.Row>
            ))}

            <Button
              variant={ButtonVariant.TERNARY}
              Icon={PlusCircleIcon}
              onClick={() => {
                arrayHelpers.push(INITIAL_PRICE_CATEGORY)
                if (values.priceCategories[0].label === UNIQUE_PRICE) {
                  setFieldValue(`priceCategories[0].label`, '')
                }
              }}
              disabled={
                values.priceCategories.length >= PRICE_CATEGORY_MAX_LENGTH
              }
            >
              Ajouter un tarif
            </Button>
          </FormLayout.Section>
        )}
      />
      <FormLayout.Section
        className={styles['duo-section']}
        title="Réservations “Duo”"
      >
        <FormLayout.Row
          sideComponent={
            <InfoBox
              type="info"
              text="Cette option permet au bénéficiaire de venir accompagné. La seconde place sera délivrée au même tarif que la première, quel que soit l'accompagnateur."
            />
          }
        >
          <Checkbox
            label="Accepter les réservations “Duo“"
            name="isDuo"
            withBorder
          />
        </FormLayout.Row>
      </FormLayout.Section>
    </>
  )
}
