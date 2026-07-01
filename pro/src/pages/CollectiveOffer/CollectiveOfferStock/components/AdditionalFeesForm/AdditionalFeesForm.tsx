import { type ChangeEvent, useState } from 'react'
import { useFieldArray, useFormContext } from 'react-hook-form'

import { CollectiveAdditionalFeeType } from '@/apiClient/v1'
import { FormLayout } from '@/components/FormLayout/FormLayout'
import { Button } from '@/design-system/Button/Button'
import { ButtonColor, ButtonVariant } from '@/design-system/Button/types'
import { RadioButtonGroup } from '@/design-system/RadioButtonGroup/RadioButtonGroup'
import { TextInput } from '@/design-system/TextInput/TextInput'
import fullMoreIcon from '@/icons/full-more.svg'
import fullTrashIcon from '@/icons/full-trash.svg'
import {
  type CustomEvent,
  SelectAutocomplete,
} from '@/ui-kit/form/SelectAutoComplete/SelectAutocomplete'

import type { CollectiveOfferStockFormValues } from '../CollectiveOfferStockForm/validationSchema'
import styles from './AdditionalFeesForm.module.scss'
import { ADDITIONAL_FEES_OPTIONS, MAX_ADDITIONAL_FEES } from './constants'

export const AdditionalFeesForm = ({
  canEditDiscount,
}: {
  canEditDiscount: boolean
}) => {
  const form = useFormContext<CollectiveOfferStockFormValues>()
  const [searchLabel, setSearchLabel] = useState<string>('')

  const hasAdditionalFees = form.watch('hasAdditionalFees')

  const { fields, append, remove } = useFieldArray({
    control: form.control,
    name: 'additionalFees',
    rules: { maxLength: MAX_ADDITIONAL_FEES },
  })

  function handleHasAdditionalFeesChange(
    event: ChangeEvent<HTMLInputElement, Element>
  ): void {
    form.setValue('hasAdditionalFees', event.target.value === 'oui', {
      shouldDirty: true,
    })
    if (event.target.value === 'non') {
      remove()
      form.setValue('additionalFees', [])
    } else if (event.target.value === 'oui' && fields.length === 0) {
      append({
        type: CollectiveAdditionalFeeType.OTHER,
        label: '',
        amount: 0,
      })
      form.setFocus('additionalFees.0.type')
    }
  }

  function handleFeeTypeChange(index: number) {
    return ({ target: { value } }: CustomEvent<'change'>) => {
      const selectedOption = ADDITIONAL_FEES_OPTIONS.find(
        (option) => option.value === value
      )
      if (selectedOption) {
        form.setValue(`additionalFees.${index}.type`, selectedOption.value, {
          shouldDirty: true,
          shouldValidate: true,
        })
        form.setValue(`additionalFees.${index}.label`, null, {
          shouldDirty: true,
          shouldValidate: true,
        })
      } else {
        form.setValue(
          `additionalFees.${index}.type`,
          CollectiveAdditionalFeeType.OTHER,
          { shouldDirty: true, shouldValidate: true }
        )
        form.setValue(`additionalFees.${index}.label`, value, {
          shouldDirty: true,
          shouldValidate: true,
        })
      }
    }
  }

  function addAdditionalFeesFieldEntry() {
    append(
      {
        type: CollectiveAdditionalFeeType.OTHER,
        label: '',
        amount: 0,
      },
      { shouldFocus: true }
    )
    setSearchLabel('')
  }

  function removeAdditionalFeesFieldEntry(index: number) {
    remove(index)
    const indexToFocus = index > 0 ? index - 1 : 0
    form.setFocus(`additionalFees.${indexToFocus}.amount`)
  }

  // We need to force dirty field evaluation at render
  // since fieldArray.remove does not dirty the field by itself properly
  const _additionalFeesDirty = form.formState.dirtyFields.additionalFees

  const matchesExistingOption = ADDITIONAL_FEES_OPTIONS.some(
    (option) => option.label === searchLabel
  )
  const creatableOption = matchesExistingOption ? undefined : searchLabel

  const shouldShowRemoveFeeButton = canEditDiscount && fields.length > 1

  return (
    <FormLayout.Row>
      <RadioButtonGroup
        label="Votre offre comprend-elle des frais annexes (ex : votre hébergement, déplacement, matériel, etc.) ?"
        name="hasAdditionalFees"
        variant="detailed"
        display="horizontal"
        sizing="hug"
        options={[
          {
            label: 'Oui',
            value: 'oui',
          },
          {
            label: 'Non',
            value: 'non',
          },
        ]}
        checkedOption={hasAdditionalFees ? 'oui' : 'non'}
        onChange={handleHasAdditionalFeesChange}
      />

      {hasAdditionalFees && (
        <div className={styles['additional-fees-container']}>
          {fields.map((field, index) => (
            <FormLayout.Row
              key={field.id}
              inline
              className={styles['additional-fee-row']}
            >
              <SelectAutocomplete
                key={field.id}
                label="Type de frais annexes"
                value={
                  field.type === CollectiveAdditionalFeeType.OTHER
                    ? (field.label ?? '')
                    : ADDITIONAL_FEES_OPTIONS.find(
                        (option) => option.value === field.type
                      )?.label
                }
                options={ADDITIONAL_FEES_OPTIONS}
                required
                name={`additionalFees.${index}`}
                className={styles['additional-fee-type-select']}
                creatableOption={creatableOption}
                onChange={handleFeeTypeChange(index)}
                onSearch={(searchText) => {
                  if (searchText.length > 0) {
                    setSearchLabel(searchText)
                  }
                }}
                error={
                  form.formState.errors?.additionalFees?.[index]?.label?.message
                }
              />
              <TextInput
                {...form.register(`additionalFees.${index}.amount`, {
                  valueAsNumber: true,
                })}
                disabled={!canEditDiscount}
                error={
                  form.formState.errors.additionalFees?.[index]?.amount?.message
                }
                min={0}
                label="Prix (en €)"
                required
                step={0.01}
                type="number"
              />

              {shouldShowRemoveFeeButton && (
                <Button
                  variant={ButtonVariant.SECONDARY}
                  color={ButtonColor.NEUTRAL}
                  icon={fullTrashIcon}
                  iconAlt={'Supprimer ce champ'}
                  onClick={() => removeAdditionalFeesFieldEntry(index)}
                  disabled={!canEditDiscount || fields.length === 1}
                />
              )}
            </FormLayout.Row>
          ))}
          {fields.length <= MAX_ADDITIONAL_FEES && (
            <Button
              variant={ButtonVariant.TERTIARY}
              icon={fullMoreIcon}
              color={ButtonColor.NEUTRAL}
              label={'Ajouter un type de frais annexes'}
              onClick={addAdditionalFeesFieldEntry}
            />
          )}
        </div>
      )}
    </FormLayout.Row>
  )
}
