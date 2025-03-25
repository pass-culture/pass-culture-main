import { useId } from 'react'
import { useFieldArray, UseFormReturn } from 'react-hook-form'

import { GetIndividualOfferWithAddressResponseModel } from 'apiClient/v1'
import { StocksCalendarFormValues } from 'components/IndividualOffer/StocksEventCreation/form/types'
import { getPriceCategoryOptions } from 'components/IndividualOffer/StocksEventEdition/getPriceCategoryOptions'
import fullMoreIcon from 'icons/full-more.svg'
import fullTrashIcon from 'icons/full-trash.svg'
import { Button } from 'ui-kit/Button/Button'
import { ButtonVariant, IconPositionEnum } from 'ui-kit/Button/types'
import { BaseInput } from 'ui-kit/form/shared/BaseInput/BaseInput'
import { FieldError } from 'ui-kit/form/shared/FieldError/FieldError'
import { Checkbox } from 'ui-kit/formV2/Checkbox/Checkbox'
import { Select } from 'ui-kit/formV2/Select/Select'

import styles from './StocksCalendarPriceCategories.module.scss'

export function StocksCalendarPriceCategories({
  form,
  priceCategories,
}: {
  form: UseFormReturn<StocksCalendarFormValues>
  priceCategories: GetIndividualOfferWithAddressResponseModel['priceCategories']
}) {
  const { fields, remove, append } = useFieldArray({
    name: 'pricingCategoriesQuantities',
  })

  const priceCategoriesOptions = getPriceCategoryOptions(priceCategories)

  const quantityErrorsId = useId()

  return (
    <>
      <h2 className={styles['title']}>Places et tarifs</h2>
      <div className={styles['price-categories']}>
        {fields.map((pricingPointQuantity, index) => {
          const registeredUnlimitedCheckbox = form.register(
            `pricingCategoriesQuantities.${index}.isUnlimited`
          )

          const registeredQuantity = form.register(
            `pricingCategoriesQuantities.${index}.quantity`
          )

          const quantityErrorId = `${quantityErrorsId}-${pricingPointQuantity.id}`
          const quantityErrorMessage =
            form.formState.errors.pricingCategoriesQuantities?.[index]?.quantity
              ?.message

          return (
            <fieldset
              key={pricingPointQuantity.id}
              className={styles['price-category-row']}
            >
              <legend className={styles['price-category-row-legend']}>
                Places et tarifs {index + 1} sur {fields.length}
              </legend>
              <div className={styles['price-category-row-quantity']}>
                <label
                  className={styles['price-category-row-quantity-label']}
                  htmlFor={`pricingCategoriesQuantities.${index}.quantity`}
                >
                  Nombre de places
                </label>
                <BaseInput
                  type="number"
                  min={0}
                  {...registeredQuantity}
                  aria-describedby={quantityErrorId}
                  onChange={async (e) => {
                    if (e.target.value) {
                      form.setValue(
                        `pricingCategoriesQuantities.${index}.isUnlimited`,
                        false
                      )
                    }

                    if (e.target.value === '') {
                      form.setValue(
                        `pricingCategoriesQuantities.${index}.isUnlimited`,
                        true
                      )
                    }
                    await registeredQuantity.onChange(e)
                  }}
                />
                <div role="alert" id={quantityErrorId}>
                  {quantityErrorMessage && (
                    <FieldError
                      className={styles['price-category-row-quantity-error']}
                      name={`pricingCategoriesQuantities.${index}.quantity`}
                    >
                      {quantityErrorMessage}
                    </FieldError>
                  )}
                </div>
              </div>
              <Checkbox
                label="Illimité"
                className={styles['price-category-row-unlimited']}
                {...registeredUnlimitedCheckbox}
                onChange={async (e) => {
                  await registeredUnlimitedCheckbox.onChange(e)

                  if (e.target.checked) {
                    form.setValue(
                      `pricingCategoriesQuantities.${index}.quantity`,
                      undefined
                    )
                  }
                }}
              />
              <Select
                className={styles['price-category-row-category']}
                options={priceCategoriesOptions}
                required
                label="Tarif"
                defaultOption={{
                  label: 'Sélectionner un tarif',
                  value: '',
                }}
                {...form.register(
                  `pricingCategoriesQuantities.${index}.priceCategory`
                )}
                error={
                  form.formState.errors.pricingCategoriesQuantities?.[index]
                    ?.priceCategory?.message
                }
              />
              {fields.length > 1 && (
                <div className={styles['price-category-row-trash']}>
                  <Button
                    variant={ButtonVariant.TERNARY}
                    icon={fullTrashIcon}
                    iconPosition={IconPositionEnum.CENTER}
                    onClick={() => {
                      remove(index)

                      const nextInput = `pricingCategoriesQuantities.${index}.quantity`
                      const previousInput = `pricingCategoriesQuantities.${index - 1}.quantity`

                      //    Focus on the next input if it exists, otherwise focus on the previous input
                      setTimeout(() => {
                        ;(
                          document.getElementById(nextInput) ||
                          document.getElementById(previousInput)
                        )?.focus()
                      })
                    }}
                    tooltipContent="Supprimer les places"
                  />
                </div>
              )}
            </fieldset>
          )
        })}
      </div>
      {fields.length < priceCategoriesOptions.length && (
        <Button
          className={styles['add-price-catgory']}
          variant={ButtonVariant.TERNARY}
          icon={fullMoreIcon}
          onClick={() => {
            append({ isUnlimited: true, priceCategory: '' })
            const inputToFocus = `pricingCategoriesQuantities.${fields.length}.quantity`

            // The input we want to focus has not been rendered first
            setTimeout(() => {
              document.getElementById(inputToFocus)?.focus()
            }, 0)
          }}
        >
          Ajouter d’autres places et tarifs
        </Button>
      )}
    </>
  )
}
