import { useFieldArray, UseFormReturn } from 'react-hook-form'

import { GetIndividualOfferWithAddressResponseModel } from 'apiClient/v1'
import { getPriceCategoryOptions } from 'components/IndividualOffer/PriceCategoriesScreen/form/getPriceCategoryOptions'
import { StocksCalendarFormValues } from 'components/IndividualOffer/StocksEventCreation/form/types'
import fullMoreIcon from 'icons/full-more.svg'
import fullTrashIcon from 'icons/full-trash.svg'
import { Button } from 'ui-kit/Button/Button'
import { ButtonVariant, IconPositionEnum } from 'ui-kit/Button/types'
import { QuantityInput } from 'ui-kit/form/QuantityInput/QuantityInput'
import { Select } from 'ui-kit/form/Select/Select'

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

  return (
    <>
      <h2 className={styles['title']}>Places et tarifs</h2>
      <div className={styles['price-categories']}>
        {fields.map((pricingPointQuantity, index) => {
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
              <div className={styles['price-category-row']}>
                <QuantityInput
                  minimum={0}
                  error={quantityErrorMessage}
                  label="Nombre de places"
                  value={form.watch(
                    `pricingCategoriesQuantities.${index}.quantity`
                  )}
                  onChange={(e) =>
                    form.setValue(
                      `pricingCategoriesQuantities.${index}.quantity`,
                      e.target.value ? Number(e.target.value) : undefined
                    )
                  }
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
              </div>
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
            append({ priceCategory: '' })
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
