import { useFieldArray, useFormContext } from 'react-hook-form'

import type { SelectOption } from '@/commons/custom_types/form'
import { FormLayout } from '@/components/FormLayout/FormLayout'
import fullMoreIcon from '@/icons/full-more.svg'
import fullTrashIcon from '@/icons/full-trash.svg'
import { Button } from '@/ui-kit/Button/Button'
import { ButtonVariant } from '@/ui-kit/Button/types'
import { QuantityInput } from '@/ui-kit/form/QuantityInput/QuantityInput'
import { Select } from '@/ui-kit/form/Select/Select'
import { ListIconButton } from '@/ui-kit/ListIconButton/ListIconButton'

import type { QuantityPerPriceCategoryForm } from '../StocksCalendar/form/types'
import styles from './QuantityPerPriceCategory.module.scss'

type QuantityPerPriceCategoryProps = {
  priceCategoryOptions: SelectOption<number>[]
}

export function QuantityPerPriceCategory({
  priceCategoryOptions,
}: QuantityPerPriceCategoryProps) {
  const { register, watch, setValue, formState } = useFormContext<{
    quantityPerPriceCategories: QuantityPerPriceCategoryForm[]
  }>()

  const { fields, append, remove } = useFieldArray({
    name: 'quantityPerPriceCategories',
  })

  return (
    <>
      {fields.map((field, index) => (
        <FormLayout.Row
          className={styles['row']}
          key={field.id}
          inline
          mdSpaceAfter
          testId={`wrapper-quantityPerPriceCategories.${index}`}
        >
          <QuantityInput
            label="Nombre de places"
            minimum={1}
            name={`quantityPerPriceCategories.${index}.quantity`}
            error={
              formState.errors.quantityPerPriceCategories?.[index]?.quantity
                ?.message
            }
            value={
              watch(`quantityPerPriceCategories.${index}.quantity`) ?? undefined
            }
            onChange={(e) => {
              setValue(
                `quantityPerPriceCategories.${index}.quantity`,
                e.target.value ? Number(e.target.value) : undefined
              )
            }}
          />
          <Select
            label="Tarif"
            options={priceCategoryOptions}
            defaultOption={{
              label: 'Sélectionner un tarif',
              value: '',
            }}
            required
            error={
              formState.errors.quantityPerPriceCategories?.[index]
                ?.priceCategory?.message
            }
            {...register(`quantityPerPriceCategories.${index}.priceCategory`)}
          />

          <div className={styles['trash']}>
            {watch('quantityPerPriceCategories').length > 1 && (
              <ListIconButton
                icon={fullTrashIcon}
                onClick={() => remove(index)}
                tooltipContent="Supprimer les places"
              />
            )}
          </div>
        </FormLayout.Row>
      ))}
      {watch('quantityPerPriceCategories').length <
        priceCategoryOptions.length && (
        <Button
          variant={ButtonVariant.TERNARY}
          icon={fullMoreIcon}
          onClick={() => append({ priceCategory: '' })}
        >
          Ajouter d’autres places et tarifs
        </Button>
      )}
    </>
  )
}
