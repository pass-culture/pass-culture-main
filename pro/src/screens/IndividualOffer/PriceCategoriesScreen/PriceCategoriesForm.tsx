import cn from 'classnames'
import type { FieldArrayRenderProps } from 'formik'
import { FieldArray, useFormikContext } from 'formik'
import { useState } from 'react'

import { api } from 'apiClient/api'
import { GetIndividualOfferResponseModel } from 'apiClient/v1'
import { ConfirmDialog } from 'components/Dialog/ConfirmDialog/ConfirmDialog'
import { FormLayout } from 'components/FormLayout/FormLayout'
import { OFFER_WIZARD_MODE } from 'core/Offers/constants'
import { useNotification } from 'hooks/useNotification'
import fullMoreIcon from 'icons/full-more.svg'
import fullTrashIcon from 'icons/full-trash.svg'
import strokeEuroIcon from 'icons/stroke-euro.svg'
import { Button } from 'ui-kit/Button/Button'
import { ButtonVariant, IconPositionEnum } from 'ui-kit/Button/types'
import { Checkbox } from 'ui-kit/form/Checkbox/Checkbox'
import { BaseCheckbox } from 'ui-kit/form/shared/BaseCheckbox/BaseCheckbox'
import { TextInput } from 'ui-kit/form/TextInput/TextInput'
import { InfoBox } from 'ui-kit/InfoBox/InfoBox'

import {
  INITIAL_PRICE_CATEGORY,
  PRICE_CATEGORY_LABEL_MAX_LENGTH,
  PRICE_CATEGORY_MAX_LENGTH,
  PRICE_CATEGORY_PRICE_MAX,
  UNIQUE_PRICE,
} from './form/constants'
import { PriceCategoriesFormValues, PriceCategoryForm } from './form/types'
import styles from './PriceCategoriesForm.module.scss'

export interface PriceCategoriesFormProps {
  offer: GetIndividualOfferResponseModel
  mode: OFFER_WIZARD_MODE
  isDisabled: boolean
  canBeDuo?: boolean
}

export const PriceCategoriesForm = ({
  offer,
  mode,
  isDisabled,
  canBeDuo,
}: PriceCategoriesFormProps): JSX.Element => {
  const { setFieldValue, values } =
    useFormikContext<PriceCategoriesFormValues>()

  const notify = useNotification()
  const [currentDeletionIndex, setCurrentDeletionIndex] = useState<
    number | null
  >(null)
  const isFreeCheckboxSelectedArray = values.priceCategories.map(
    (priceCategory) => priceCategory.price === 0
  )

  const onDeletePriceCategory = async (
    index: number,
    arrayHelpers: FieldArrayRenderProps,
    priceCategories: PriceCategoryForm[],
    priceCategoryId?: number
  ) => {
    if (priceCategoryId) {
      if (currentDeletionIndex === null && offer.hasStocks) {
        setCurrentDeletionIndex(index)
        return
      } else {
        setCurrentDeletionIndex(null)
      }
      try {
        await api.deletePriceCategory(offer.id, priceCategoryId)
        arrayHelpers.remove(index)
        notify.success('Le tarif a été supprimé.')
      } catch {
        notify.error(
          'Une erreur est survenue lors de la suppression de votre tarif'
        )
      }
    } else {
      arrayHelpers.remove(index)
    }

    if (values.priceCategories.length === 2) {
      await setFieldValue(`priceCategories[0].label`, UNIQUE_PRICE)
      const otherPriceCategory = priceCategories.filter(
        (pC) => pC.id !== priceCategoryId
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
        try {
          await api.postPriceCategories(offer.id, requestBody)
        } catch (error) {
          notify.error(
            'Une erreur est survenue lors de la mise à jour de votre tarif'
          )
        }
      }
    }
  }

  return (
    <>
      <FormLayout>
        <FormLayout.MandatoryInfo />
        <FieldArray
          name="priceCategories"
          render={(arrayHelpers) => (
            <FormLayout.Section title="Tarifs">
              {currentDeletionIndex !== null && (
                <ConfirmDialog
                  onCancel={() => setCurrentDeletionIndex(null)}
                  onConfirm={() =>
                    onDeletePriceCategory(
                      currentDeletionIndex,
                      arrayHelpers,
                      values.priceCategories,
                      values.priceCategories[currentDeletionIndex]?.id
                    )
                  }
                  title="En supprimant ce tarif vous allez aussi supprimer l’ensemble des dates qui lui sont associées."
                  confirmText="Confirmer la supression"
                  cancelText="Annuler"
                />
              )}
              {values.priceCategories.map((priceCategory, index) => (
                <FormLayout.Row
                  key={index}
                  inline
                  smSpaceAfter
                  className={styles['form-layout-row-price-category']}
                >
                  <TextInput
                    smallLabel
                    name={`priceCategories[${index}].label`}
                    label="Intitulé du tarif"
                    placeholder="Ex : catégorie 2, moins de 18 ans, pass 3 jours..."
                    maxLength={PRICE_CATEGORY_LABEL_MAX_LENGTH}
                    countCharacters
                    className={styles['label-input']}
                    disabled={values.priceCategories.length <= 1 || isDisabled}
                  />

                  <TextInput
                    smallLabel
                    name={`priceCategories[${index}].price`}
                    label="Prix par personne"
                    type="number"
                    step="0.01"
                    max={PRICE_CATEGORY_PRICE_MAX}
                    rightIcon={strokeEuroIcon}
                    className={styles['price-input']}
                    disabled={isDisabled}
                  />

                  <div className={cn(styles['form-row-actions'])}>
                    <BaseCheckbox
                      className={styles['free-checkbox']}
                      label="Gratuit"
                      checked={isFreeCheckboxSelectedArray[index]}
                      name={`priceCategories[${index}].free`}
                      onChange={async (e) => {
                        if (e.target.checked) {
                          await setFieldValue(
                            `priceCategories[${index}].price`,
                            0
                          )
                        } else {
                          await setFieldValue(
                            `priceCategories[${index}].price`,
                            ''
                          )
                        }
                      }}
                      disabled={isDisabled}
                    />
                    {mode === OFFER_WIZARD_MODE.CREATION && (
                      <Button
                        className={styles['delete-icon']}
                        data-testid={'delete-button'}
                        variant={ButtonVariant.TERNARY}
                        icon={fullTrashIcon}
                        iconPosition={IconPositionEnum.CENTER}
                        disabled={
                          values.priceCategories.length <= 1 || isDisabled
                        }
                        onClick={() =>
                          onDeletePriceCategory(
                            index,
                            arrayHelpers,
                            values.priceCategories,
                            values.priceCategories[index]?.id
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
                icon={fullMoreIcon}
                onClick={async () => {
                  arrayHelpers.push(INITIAL_PRICE_CATEGORY)
                  if (values.priceCategories[0]?.label === UNIQUE_PRICE) {
                    await setFieldValue(`priceCategories[0].label`, '')
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
        <FormLayout fullWidthActions>
          <FormLayout.Section
            className={styles['duo-section']}
            title="Réservations “Duo”"
          >
            <FormLayout.Row
              sideComponent={
                <InfoBox>
                  Cette option permet au bénéficiaire de venir accompagné. La
                  seconde place sera délivrée au même tarif que la première,
                  quel que soit l’accompagnateur.
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
