import { useRef, useState } from 'react'
import { useFieldArray, useFormContext } from 'react-hook-form'

import type { GetIndividualOfferWithAddressResponseModel } from '@/apiClient/v1'
import { OFFER_WIZARD_MODE } from '@/commons/core/Offers/constants'
import { assertOrFrontendError } from '@/commons/errors/assertOrFrontendError'
import { getDepartmentCode } from '@/commons/utils/getDepartmentCode'
import { toNumberOrNull } from '@/commons/utils/toNumberOrNull'
import { DialogStockThingDeleteConfirm } from '@/components/IndividualOffer/DialogStockDeleteConfirm/DialogStockThingDeleteConfirm'
import { ActivationCodeFormDialog } from '@/components/IndividualOffer/StocksThing/ActivationCodeFormDialog/ActivationCodeFormDialog'
import fullCodeIcon from '@/icons/full-code.svg'
import fulleMoreIcon from '@/icons/full-more.svg'
import fullTrashIcon from '@/icons/full-trash.svg'
import strokeEuroIcon from '@/icons/stroke-euro.svg'
import strokeFrancIcon from '@/icons/stroke-franc.svg'
import { Button } from '@/ui-kit/Button/Button'
import { ButtonVariant } from '@/ui-kit/Button/types'
import { PriceInput } from '@/ui-kit/form/PriceInput/PriceInput'
import { QuantityInput } from '@/ui-kit/form/QuantityInput/QuantityInput'
import { TextInput } from '@/ui-kit/form/TextInput/TextInput'
import { ListIconButton } from '@/ui-kit/ListIconButton/ListIconButton'

import {
  PriceTableEntryValidationSchema,
  type PriceTableFormValues,
} from '../../commons/schemas'
import type { PriceTableFormContext } from '../../commons/types'
import { getFieldsSpecs } from '../../commons/utils/getFieldsSpecs'
import styles from './PriceTableForm.module.scss'

interface PriceTableFormProps {
  isCaledonian: boolean
  isReadOnly?: boolean
  mode: OFFER_WIZARD_MODE
  offer: GetIndividualOfferWithAddressResponseModel
  schemaValidationContext: PriceTableFormContext
}
export const PriceTableForm = ({
  isCaledonian,
  isReadOnly = false,
  mode,
  offer,
  schemaValidationContext,
}: PriceTableFormProps) => {
  const activationCodeButtonRef = useRef<HTMLButtonElement>(null)

  const {
    control,
    getValues,
    watch,
    register,
    setValue,
    formState: { errors },
  } = useFormContext<PriceTableFormValues>()
  const { fields, append, remove } = useFieldArray({
    control,
    name: 'entries',
  })

  const [
    activationCodeEntryIndexToUpload,
    setActivationCodeEntryIndexToUpload,
  ] = useState<number | null>(null)
  const [entryIndexToConfirmAndRemove, setEntryIndexToConfirmAndRemove] =
    useState<number | null>(null)

  const entries = watch('entries')

  const { minExpirationDate, minQuantity, nowAsDate } = getFieldsSpecs({
    entries,
    offer,
    mode,
  })

  const addEntry = () => {
    const newRow = PriceTableEntryValidationSchema.cast(
      { offerId: offer.id },
      { assert: false, context: schemaValidationContext }
    )

    append(newRow, { shouldFocus: true })
  }

  const removeEntry = (indexToRemove: number) => {
    assertOrFrontendError(
      fields.length > 1,
      '`removeEntry` should not be called when there is only one entry.'
    )

    if (fields.length === 2) {
      const indexToKeep = indexToRemove === 0 ? 1 : 0

      setValue(`entries.${indexToKeep}.label`, 'Tarif unique')
    }

    remove(indexToRemove)
  }

  const askForRemovalConfirmationOrRemove = (indexToRemove: number) => {
    assertOrFrontendError(
      fields.length > 1,
      '`askForRemovalConfirmationOrRemove` should not be called when there is only one entry.'
    )

    const entryToRemove = getValues(`entries.${indexToRemove}`)

    if (
      mode === OFFER_WIZARD_MODE.EDITION &&
      typeof entryToRemove.id === 'number' &&
      entryToRemove.bookingsQuantity &&
      entryToRemove.bookingsQuantity > 0
    ) {
      setEntryIndexToConfirmAndRemove(indexToRemove)
    } else {
      removeEntry(indexToRemove)
    }
  }

  const uploadActivationCodes = (
    activationCodes: string[],
    expirationDate: string | undefined
  ) => {
    assertOrFrontendError(
      typeof activationCodeEntryIndexToUpload === 'number',
      '`activationCodeEntryIndexToUpload` should be a number when submitting activation codes.'
    )

    setValue(
      `entries.${activationCodeEntryIndexToUpload}.quantity`,
      activationCodes.length
    )
    setValue(
      `entries.${activationCodeEntryIndexToUpload}.activationCodes`,
      activationCodes
    )
    setValue(
      `entries.${activationCodeEntryIndexToUpload}.activationCodesExpirationDatetime`,
      expirationDate ?? null
    )

    setActivationCodeEntryIndexToUpload(null)
  }

  return (
    <>
      {entryIndexToConfirmAndRemove !== null && (
        <DialogStockThingDeleteConfirm
          onConfirm={() => removeEntry(entryIndexToConfirmAndRemove)}
          onCancel={() => setEntryIndexToConfirmAndRemove(null)}
          isDialogOpen
        />
      )}

      {activationCodeEntryIndexToUpload !== null && (
        <ActivationCodeFormDialog
          onSubmit={uploadActivationCodes}
          onCancel={() => setActivationCodeEntryIndexToUpload(null)}
          today={nowAsDate}
          minExpirationDate={minExpirationDate}
          isDialogOpen
          activationCodeButtonRef={activationCodeButtonRef}
          departmentCode={getDepartmentCode(offer)}
        />
      )}

      {fields.map((field, index) => (
        <div key={field.id} className={styles['row']}>
          {offer.isEvent && (
            <TextInput
              {...register(`entries.${index}.label`)}
              className={styles['input-label']}
              disabled={fields.length <= 1 || isReadOnly}
              error={errors.entries?.[index]?.label?.message}
              label="Intitulé du tarif"
            />
          )}

          <PriceInput
            {...register(`entries.${index}.price`)}
            data-testid={`price-row-${index}-price`}
            disabled={isReadOnly}
            error={errors.entries?.[index]?.price?.message}
            label="Prix"
            rightIcon={isCaledonian ? strokeFrancIcon : strokeEuroIcon}
            showFreeCheckbox
            updatePriceValue={(value) =>
              void setValue(`entries.${index}.price`, Number(value), {
                shouldDirty: true,
              })
            }
          />

          {!offer.isEvent && (
            <QuantityInput
              className={styles['field-layout-small']}
              disabled={isReadOnly}
              error={errors.entries?.[index]?.quantity?.message}
              label="Stock"
              minimum={minQuantity}
              onChange={(e) =>
                void setValue(
                  `entries.${index}.quantity`,
                  toNumberOrNull(e.target.value),
                  {
                    shouldDirty: true,
                  }
                )
              }
              required
              value={watch(`entries.${index}.quantity`)}
            />
          )}

          {!offer.isEvent && offer.isDigital && (
            <ListIconButton
              className={styles['button-action']}
              dataTestid="action-addActivationCode"
              icon={fullCodeIcon}
              onClick={() => setActivationCodeEntryIndexToUpload(index)}
              readOnly={isReadOnly}
              ref={activationCodeButtonRef}
              tooltipContent="Ajouter des codes d'activation"
            />
          )}

          {!offer.isEvent &&
            mode === OFFER_WIZARD_MODE.EDITION &&
            entries.length > 0 && (
              <>
                <TextInput
                  className={styles['input-readonly--first']}
                  hasLabelLineBreak={false}
                  isOptional
                  label="Stock restant"
                  name="availableStock"
                  readOnly
                  smallLabel
                  value={
                    getValues(`entries.${index}.remainingQuantity`) ===
                    'unlimited'
                      ? 'Illimité'
                      : (getValues(`entries.${index}.remainingQuantity`) ??
                        undefined)
                  }
                />

                <TextInput
                  {...register(`entries.${index}.bookingsQuantity`)}
                  className={styles['input-readonly']}
                  isOptional
                  label="Réservations"
                  readOnly
                  smallLabel
                  value={getValues(`entries.${index}.bookingsQuantity`) || 0}
                />
              </>
            )}

          {fields.length > 1 && (
            <ListIconButton
              className={styles['button-action']}
              icon={fullTrashIcon}
              onClick={() => askForRemovalConfirmationOrRemove(index)}
              tooltipContent="Supprimer ce tarif"
            />
          )}
        </div>
      ))}

      {offer.isEvent && (
        <div className={styles['row']}>
          <Button
            disabled={isReadOnly}
            icon={fulleMoreIcon}
            onClick={addEntry}
            type="button"
            variant={ButtonVariant.TERNARY}
          >
            Ajouter un tarif
          </Button>
        </div>
      )}
    </>
  )
}
