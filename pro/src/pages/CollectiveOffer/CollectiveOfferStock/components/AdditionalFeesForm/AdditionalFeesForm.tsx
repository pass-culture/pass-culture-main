import { type ChangeEvent, useState } from 'react'
import { flushSync } from 'react-dom'
import { type FieldError, useFieldArray, useFormContext } from 'react-hook-form'

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
import {
  ADDITIONAL_FEES_OPTIONS,
  MAX_ADDITIONAL_FEES_LENGHT,
} from './constants'

function dispatchRootError(rootFieldError: FieldError | undefined) {
  let rootErrorOnTypes = ''
  let rootErrorOnAmounts = ''
  if (!rootFieldError) {
    return { rootErrorOnTypes, rootErrorOnAmounts }
  }
  const msg = rootFieldError.message || ''
  if (rootFieldError.type.includes('price')) {
    rootErrorOnAmounts = msg
  }
  if (/(type|label)/.test(rootFieldError.type)) {
    rootErrorOnTypes = msg
  }
  if (rootFieldError.type === 'custom') {
    //comes from the API
    if (/(type|label)/.test(msg)) {
      rootErrorOnTypes = msg
    } else {
      rootErrorOnAmounts = msg
    }
  }
  return { rootErrorOnTypes, rootErrorOnAmounts }
}

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
    name: 'collectiveAdditionalFees',
    rules: { maxLength: MAX_ADDITIONAL_FEES_LENGHT },
  })

  function handleHasAdditionalFeesChange(
    event: ChangeEvent<HTMLInputElement, Element>
  ): void {
    form.setValue('hasAdditionalFees', event.target.value === 'oui', {
      shouldDirty: true,
    })
    if (event.target.value === 'non') {
      remove()
      form.setValue('collectiveAdditionalFees', [])
    } else if (event.target.value === 'oui' && fields.length === 0) {
      append({
        type: CollectiveAdditionalFeeType.OTHER,
        label: '',
        amount: 0,
      })
      form.setFocus('collectiveAdditionalFees.0.type')
    }
  }

  function handleFeeTypeChange(index: number) {
    return ({ target: { value } }: CustomEvent<'change'>) => {
      const selectedOption = ADDITIONAL_FEES_OPTIONS.find(
        (option) => option.value === value
      )
      if (selectedOption) {
        form.setValue(
          `collectiveAdditionalFees.${index}.type`,
          selectedOption.value,
          {
            shouldDirty: true,
            shouldValidate: true,
          }
        )
        form.setValue(`collectiveAdditionalFees.${index}.label`, null, {
          shouldDirty: true,
          shouldValidate: true,
        })
      } else {
        form.setValue(
          `collectiveAdditionalFees.${index}.type`,
          CollectiveAdditionalFeeType.OTHER,
          { shouldDirty: true, shouldValidate: true }
        )
        form.setValue(`collectiveAdditionalFees.${index}.label`, value, {
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
    return () => {
      flushSync(() => remove(index))
      const indexToFocus = Math.min(
        index,
        form.getValues('collectiveAdditionalFees').length
      )
      form.setFocus(`collectiveAdditionalFees.${indexToFocus}.amount`)
    }
  }

  // We need to force dirty field evaluation at render
  // since fieldArray.remove does not dirty the field by itself properly
  const _additionalFeesDirty =
    form.formState.dirtyFields.collectiveAdditionalFees

  const matchesExistingOption = ADDITIONAL_FEES_OPTIONS.some(
    (option) => option.label === searchLabel
  )
  const creatableOption = matchesExistingOption ? undefined : searchLabel

  const shouldShowRemoveFeeButton = canEditDiscount && fields.length > 1
  const shouldShowAddFeeButton =
    canEditDiscount && fields.length <= MAX_ADDITIONAL_FEES_LENGHT

  // errors that we display on each amount or type field
  const { rootErrorOnTypes, rootErrorOnAmounts } = dispatchRootError(
    form.formState.errors.collectiveAdditionalFees?.root
  )

  return (
    <FormLayout.Row>
      <RadioButtonGroup
        label="Votre offre comprend-elle des frais annexes (ex : votre hébergement, déplacement, matériel, etc.) ?"
        name="hasAdditionalFees"
        variant="detailed"
        display="horizontal"
        disabled={!canEditDiscount}
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
              <AdditionalFeesInput
                field={field}
                index={index}
                canEditDiscount={canEditDiscount}
                form={form}
                setSearchLabel={setSearchLabel}
                creatableOption={creatableOption}
                handleFeeTypeChange={handleFeeTypeChange}
                rootErrorOnTypes={rootErrorOnTypes}
                value={form.watch(`collectiveAdditionalFees.${index}.type`)}
              />
              <TextInput
                {...form.register(`collectiveAdditionalFees.${index}.amount`, {
                  valueAsNumber: true,
                  onChange: () =>
                    form.trigger(['collectiveAdditionalFees', 'servicePrice']),
                })}
                disabled={!canEditDiscount}
                error={
                  rootErrorOnAmounts ||
                  form.formState.errors.collectiveAdditionalFees?.[index]
                    ?.amount?.message
                }
                label="Prix (en €)"
                min={0.01}
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
                  onClick={removeAdditionalFeesFieldEntry(index)}
                  disabled={!canEditDiscount || fields.length === 1}
                />
              )}
            </FormLayout.Row>
          ))}
          {shouldShowAddFeeButton && (
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

type AdditionalFeesInputProps = {
  field: { type: CollectiveAdditionalFeeType; label?: string | null }
  index: number
  canEditDiscount: boolean
  form: ReturnType<typeof useFormContext<CollectiveOfferStockFormValues>>
  setSearchLabel: (label: string) => void
  creatableOption?: string
  handleFeeTypeChange: (index: number) => (value: CustomEvent<'change'>) => void
  rootErrorOnTypes: string
  value?: CollectiveAdditionalFeeType | string | null
}

function AdditionalFeesInput({
  field,
  index,
  canEditDiscount,
  form,
  setSearchLabel,
  creatableOption,
  handleFeeTypeChange,
  rootErrorOnTypes,
  value: currentValue,
}: Readonly<AdditionalFeesInputProps>) {
  const getDisplayValueFrom = (
    feeType: CollectiveAdditionalFeeType | string | null | undefined,
    feeLabel: string | null | undefined
  ) => {
    if (feeType === CollectiveAdditionalFeeType.OTHER) {
      return feeLabel ?? ''
    }

    return (
      ADDITIONAL_FEES_OPTIONS.find((option) => option.value === feeType)
        ?.label ?? ''
    )
  }

  const getDisplayValue = () => {
    const feeType = form.getValues(`collectiveAdditionalFees.${index}.type`)
    const feeLabel = form.getValues(`collectiveAdditionalFees.${index}.label`)

    return getDisplayValueFrom(feeType, feeLabel)
  }

  const [value, setValue] = useState(
    getDisplayValueFrom(currentValue ?? field.type, field.label)
  )

  return (
    <SelectAutocomplete
      label="Type de frais annexes"
      options={ADDITIONAL_FEES_OPTIONS.filter(
        (o) => o.value !== CollectiveAdditionalFeeType.OTHER
      )}
      required
      disabled={!canEditDiscount}
      name={`collectiveAdditionalFees.${index}.type`}
      className={styles['additional-fee-type-select']}
      creatableOption={creatableOption}
      onChange={handleFeeTypeChange(index)}
      onSearch={setSearchLabel}
      onBlur={(event) => {
        if (!event.target.value) {
          setValue('')
          setSearchLabel('')
          return
        }

        setValue(getDisplayValue())
        setSearchLabel('')
      }}
      error={
        rootErrorOnTypes ||
        form.formState.errors.collectiveAdditionalFees?.[index]?.type
          ?.message ||
        form.formState.errors.collectiveAdditionalFees?.[index]?.label?.message
      }
      // use this to control focus on input
      ref={form.register(`collectiveAdditionalFees.${index}.type`).ref}
      value={value}
    />
  )
}
