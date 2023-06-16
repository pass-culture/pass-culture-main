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
import { PlusCircleIcon, TrashFilledIcon } from 'icons'
import { ReactComponent as StrokeEuro } from 'icons/stroke-euro.svg'
import { Button, Checkbox, InfoBox, TextInput } from 'ui-kit'
import { ButtonVariant, IconPositionEnum } from 'ui-kit/Button/types'
import { BaseCheckbox } from 'ui-kit/form/shared'

import deletePriceCategoryAdapter from './adapters/deletePriceCategoryAdapter'
import postPriceCategoriesAdapter from './adapters/postPriceCategoriesAdapter'
import { computeInitialValues } from './form/computeInitialValues'
import {
  INITIAL_PRICE_CATEGORY,
  PRICE_CATEGORY_LABEL_MAX_LENGTH,
  PRICE_CATEGORY_MAX_LENGTH,
  PRICE_CATEGORY_PRICE_MAX,
  UNIQUE_PRICE,
} from './form/constants'
import { PriceCategoriesFormValues, PriceCategoryForm } from './form/types'
import styles from './PriceCategoriesForm.module.scss'

interface IPriceCategoriesForm {
  offerId: number
  stocks: IOfferIndividualStock[]
  mode: OFFER_WIZARD_MODE
  setOffer: ((offer: IOfferIndividual | null) => void) | null
  isDisabled: boolean
  canBeDuo?: boolean
}

export const PriceCategoriesForm = ({
  offerId,
  stocks,
  mode,
  setOffer,
  isDisabled,
  canBeDuo,
}: IPriceCategoriesForm): JSX.Element => {
  const { setFieldValue, setValues, values } =
    useFormikContext<PriceCategoriesFormValues>()
  const notify = useNotification()
  const [currentDeletionIndex, setCurrentDeletionIndex] = useState<
    number | null
  >(null)
  const isFreeCheckboxSelectedArray = values.priceCategories.map(
    priceCategory => priceCategory.price === 0
  )

  const onChangeFree =
    (index: number) => (e: React.ChangeEvent<HTMLInputElement>) => {
      if (e.target.checked) {
        setFieldValue(`priceCategories[${index}].price`, 0)
      } else {
        setFieldValue(`priceCategories[${index}].price`, '')
      }
    }

  const onDeletePriceCategory = async (
    index: number,
    arrayHelpers: FieldArrayRenderProps,
    priceCategories: PriceCategoryForm[],
    priceCategoryId?: number
  ) => {
    if (priceCategoryId) {
      const shouldDisplayConfirmDeletePriceCategory = stocks.some(
        stock => stock.priceCategoryId === priceCategoryId
      )
      if (
        currentDeletionIndex === null &&
        shouldDisplayConfirmDeletePriceCategory
      ) {
        setCurrentDeletionIndex(index)
        return
      } else {
        setCurrentDeletionIndex(null)
      }
      const { isOk, message } = await deletePriceCategoryAdapter({
        offerId,
        priceCategoryId: priceCategoryId,
      })
      if (isOk) {
        arrayHelpers.remove(index)
        const response = await getOfferIndividualAdapter(offerId)
        if (response.isOk) {
          const updatedOffer = response.payload
          setOffer && setOffer(updatedOffer)
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
      const otherPriceCategory = priceCategories.filter(
        pC => pC.id !== priceCategoryId
      )
      const otherPriceCategoryId = otherPriceCategory[0]?.id
      if (otherPriceCategoryId) {
        const requestBody = {
          priceCategories: [
            {
              label: UNIQUE_PRICE,
              id: otherPriceCategoryId,
            },
          ],
        }
        await postPriceCategoriesAdapter({
          offerId: offerId,
          requestBody: requestBody,
        })
      }
      const response = await getOfferIndividualAdapter(offerId)
      if (response.isOk) {
        const updatedOffer = response.payload
        setOffer && setOffer(updatedOffer)
        setValues({
          ...values,
          priceCategories: computeInitialValues(updatedOffer).priceCategories,
        })
      }
    }
  }

  return (
    <>
      <FormLayout>
        <FormLayout.MandatoryInfo />
        <FieldArray
          name="priceCategories"
          render={arrayHelpers => (
            <FormLayout.Section title="Tarifs">
              {currentDeletionIndex !== null && (
                <ConfirmDialog
                  onCancel={() => setCurrentDeletionIndex(null)}
                  onConfirm={() =>
                    onDeletePriceCategory(
                      currentDeletionIndex,
                      arrayHelpers,
                      values.priceCategories,
                      values.priceCategories[currentDeletionIndex].id
                    )
                  }
                  title="En supprimant ce tarif vous allez aussi supprimer l’ensemble des occurrences qui lui sont associées."
                  confirmText="Confirmer la supression"
                  cancelText="Annuler"
                />
              )}
              {values.priceCategories.map((priceCategory, index) => (
                <FormLayout.Row key={index} inline smSpaceAfter>
                  <TextInput
                    smallLabel
                    name={`priceCategories[${index}].label`}
                    label="Intitulé du tarif"
                    placeholder="Ex : catégorie 2, moins de 18 ans, pass 3 jours..."
                    maxLength={PRICE_CATEGORY_LABEL_MAX_LENGTH}
                    countCharacters
                    className={styles['label-input']}
                    disabled={values.priceCategories.length <= 1 || isDisabled}
                    isLabelHidden={index !== 0}
                  />

                  <TextInput
                    smallLabel
                    name={`priceCategories[${index}].price`}
                    label="Prix par personne"
                    type="number"
                    step="0.01"
                    max={PRICE_CATEGORY_PRICE_MAX}
                    rightIcon={() => <StrokeEuro />}
                    className={styles['price-input']}
                    isLabelHidden={index !== 0}
                    disabled={isDisabled}
                  />

                  <div
                    className={cn(styles['form-row-actions'], {
                      [styles['first-row']]: index === 0,
                    })}
                  >
                    <BaseCheckbox
                      className={styles['free-checkbox']}
                      label="Gratuit"
                      checked={isFreeCheckboxSelectedArray[index]}
                      name={`priceCategories[${index}].free`}
                      onChange={onChangeFree(index)}
                      disabled={isDisabled}
                    />
                    {mode !== OFFER_WIZARD_MODE.EDITION && (
                      <Button
                        className={styles['delete-icon']}
                        data-testid={'delete-button'}
                        variant={ButtonVariant.TERNARY}
                        Icon={TrashFilledIcon}
                        iconPosition={IconPositionEnum.CENTER}
                        disabled={
                          values.priceCategories.length <= 1 || isDisabled
                        }
                        onClick={() =>
                          onDeletePriceCategory(
                            index,
                            arrayHelpers,
                            values.priceCategories,
                            values.priceCategories[index].id
                          )
                        }
                        hasTooltip={
                          values.priceCategories.length > 1 && !isDisabled
                        }
                      >
                        {values.priceCategories.length > 1 &&
                          !isDisabled &&
                          'Supprimer le tarif'}
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
                  values.priceCategories.length >= PRICE_CATEGORY_MAX_LENGTH ||
                  isDisabled
                }
              >
                Ajouter un tarif
              </Button>
            </FormLayout.Section>
          )}
        />
      </FormLayout>

      {canBeDuo && (
        <FormLayout small>
          <FormLayout.Section
            className={styles['duo-section']}
            title="Réservations “Duo”"
          >
            <FormLayout.Row
              sideComponent={
                <InfoBox>
                  Cette option permet au bénéficiaire de venir accompagné. La
                  seconde place sera délivrée au même tarif que la première,
                  quel que soit l'accompagnateur.
                </InfoBox>
              }
            >
              <Checkbox
                label="Accepter les réservations “Duo“"
                name="isDuo"
                disabled={isDisabled}
                withBorder
              />
            </FormLayout.Row>
          </FormLayout.Section>
        </FormLayout>
      )}
    </>
  )
}
