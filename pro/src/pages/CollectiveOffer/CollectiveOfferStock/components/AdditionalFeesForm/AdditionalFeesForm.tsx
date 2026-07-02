import type { ChangeEvent } from 'react'
import { useRef } from 'react'
import { flushSync } from 'react-dom'
import { type FieldError, useFieldArray, useFormContext } from 'react-hook-form'

import {
  type CollectiveAdditionalFeeModel,
  CollectiveAdditionalFeeType,
} from '@/apiClient/v1'
import { FormLayout } from '@/components/FormLayout/FormLayout'
import { Button } from '@/design-system/Button/Button'
import { ButtonColor, ButtonVariant } from '@/design-system/Button/types'
import { RadioButtonGroup } from '@/design-system/RadioButtonGroup/RadioButtonGroup'
import { TextInput } from '@/design-system/TextInput/TextInput'
import fullMoreIcon from '@/icons/full-more.svg'
import fullTrashIcon from '@/icons/full-trash.svg'

import type { CollectiveOfferStockFormValues } from '../CollectiveOfferStockForm/validationSchema'
import styles from './AdditionalFeesForm.module.scss'
import { AdditionalFeeTypeInput } from './components/AdditionalFeeTypeInput/AdditionalFeeTypeInput'
import { MAX_ADDITIONAL_FEES_LENGTH } from './constants'

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

  const hasAdditionalFees = form.watch('hasAdditionalFees')

  const { fields, append, remove } = useFieldArray({
    control: form.control,
    name: 'collectiveAdditionalFees',
    rules: { maxLength: MAX_ADDITIONAL_FEES_LENGTH },
  })

  const typeInputElements = useRef<(HTMLInputElement | null)[]>([])

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
      typeInputElements.current[0]?.focus()
    }
  }

  function handleFeeTypeChange(index: number) {
    return ({ type, label }: Omit<CollectiveAdditionalFeeModel, 'amount'>) => {
      form.setValue(`collectiveAdditionalFees.${index}.type`, type, {
        shouldDirty: true,
      })
      form.setValue(`collectiveAdditionalFees.${index}.label`, label, {
        shouldDirty: true,
        shouldTouch: true,
      })
      form.trigger('collectiveAdditionalFees')
    }
  }

  function addAdditionalFeesFieldEntry() {
    flushSync(() => {
      append({
        type: CollectiveAdditionalFeeType.OTHER,
        label: '',
        amount: 0,
      })
    })
    const newIndex = form.getValues('collectiveAdditionalFees').length - 1
    typeInputElements.current[newIndex]?.focus()
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

  const shouldShowRemoveFeeButton = canEditDiscount && fields.length > 1
  const shouldShowAddFeeButton =
    canEditDiscount && fields.length < MAX_ADDITIONAL_FEES_LENGTH

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
              <AdditionalFeeTypeInput
                collectiveAdditionalFee={field}
                disabled={!canEditDiscount}
                name={`collectiveAdditionalFees.${index}.type`}
                className={styles['additional-fee-type-select']}
                onChange={handleFeeTypeChange(index)}
                ref={(el) => {
                  typeInputElements.current[index] = el
                }}
                error={
                  rootErrorOnTypes ||
                  form.formState.errors.collectiveAdditionalFees?.[index]?.type
                    ?.message ||
                  form.formState.errors.collectiveAdditionalFees?.[index]?.label
                    ?.message
                }
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
                <div className={styles['remove-button-container']}>
                  <Button
                    variant={ButtonVariant.SECONDARY}
                    color={ButtonColor.NEUTRAL}
                    icon={fullTrashIcon}
                    iconAlt={'Supprimer ce champ'}
                    onClick={removeAdditionalFeesFieldEntry(index)}
                    disabled={!canEditDiscount || fields.length === 1}
                  />
                </div>
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
