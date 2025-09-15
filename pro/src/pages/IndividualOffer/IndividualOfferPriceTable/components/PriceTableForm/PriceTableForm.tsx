import classNames from 'classnames'
import { useRef, useState } from 'react'
import { useFieldArray, useFormContext } from 'react-hook-form'

import type { GetIndividualOfferWithAddressResponseModel } from '@/apiClient/v1'
import { OFFER_WIZARD_MODE } from '@/commons/core/Offers/constants'
import { assertOrFrontendError } from '@/commons/errors/assertOrFrontendError'
import { isDateValid } from '@/commons/utils/date'
import { getDepartmentCode } from '@/commons/utils/getDepartmentCode'
import { toNumberOrNull } from '@/commons/utils/toNumberOrNull'
import { ActivationCodeFormDialog } from '@/components/IndividualOffer/StocksThing/ActivationCodeFormDialog/ActivationCodeFormDialog'
import fullCodeIcon from '@/icons/full-code.svg'
import fulleMoreIcon from '@/icons/full-more.svg'
import fullTrashIcon from '@/icons/full-trash.svg'
import strokeEuroIcon from '@/icons/stroke-euro.svg'
import strokeFrancIcon from '@/icons/stroke-franc.svg'
import { DialogStockThingDeleteConfirm } from '@/pages/IndividualOffer/components/DialogStockThingDeleteConfirm/DialogStockThingDeleteConfirm'
import { Button } from '@/ui-kit/Button/Button'
import { ButtonVariant } from '@/ui-kit/Button/types'
import { DatePicker } from '@/ui-kit/form/DatePicker/DatePicker'
import { PriceInput } from '@/ui-kit/form/PriceInput/PriceInput'
import { QuantityInput } from '@/ui-kit/form/QuantityInput/QuantityInput'
import { TextInput } from '@/ui-kit/form/TextInput/TextInput'
import { ListIconButton } from '@/ui-kit/ListIconButton/ListIconButton'

import { PRICE_TABLE_ENTRY_MAX_LABEL_LENGTH } from '../../commons/constants'
import {
  PriceTableEntryValidationSchema,
  type PriceTableFormValues,
} from '../../commons/schemas'
import type { PriceTableFormContext } from '../../commons/types'
import { makeFieldConstraints } from '../../commons/utils/makeFieldConstraints'
import styles from './PriceTableForm.module.scss'

export interface PriceTableFormProps {
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

  const { computeEntryConstraints, nowAsDate } = makeFieldConstraints({
    offer,
    mode,
  })

  const firstEntry = watch('entries.0')
  const activationCodesExpirationDatetimeMin = firstEntry
    ? computeEntryConstraints(firstEntry).activationCodesExpirationDatetimeMin
    : null

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
      <DialogStockThingDeleteConfirm
        isDialogOpen={entryIndexToConfirmAndRemove !== null}
        onCancel={() => setEntryIndexToConfirmAndRemove(null)}
        onConfirm={() =>
          entryIndexToConfirmAndRemove
            ? removeEntry(entryIndexToConfirmAndRemove)
            : null
        }
      />

      <ActivationCodeFormDialog
        activationCodeButtonRef={activationCodeButtonRef}
        departmentCode={getDepartmentCode(offer)}
        isDialogOpen={activationCodeEntryIndexToUpload !== null}
        minExpirationDate={activationCodesExpirationDatetimeMin}
        onCancel={() => setActivationCodeEntryIndexToUpload(null)}
        onSubmit={uploadActivationCodes}
        today={nowAsDate}
      />

      {fields.map((field, index) => {
        const entry = watch(`entries.${index}`)

        return (
          <div
            key={field.id}
            className={classNames(styles['row'], {
              [styles['event']]: offer.isEvent,
            })}
          >
            {offer.isEvent && (
              <TextInput
                {...register(`entries.${index}.label`)}
                autoComplete="off"
                className={styles['input-label']}
                disabled={fields.length <= 1 || isReadOnly}
                error={errors.entries?.[index]?.label?.message}
                label="Intitulé du tarif"
                maxLength={PRICE_TABLE_ENTRY_MAX_LABEL_LENGTH}
                count={entry.label?.length || 0}
                description="Par exemple : catégorie 2, moins de 18 ans, pass 3 jours..."
              />
            )}

            <PriceInput
              {...register(`entries.${index}.price`)}
              className={styles['input-price']}
              disabled={isReadOnly}
              error={errors.entries?.[index]?.price?.message}
              label="Prix"
              rightIcon={isCaledonian ? strokeFrancIcon : strokeEuroIcon}
              showFreeCheckbox
              updatePriceValue={(value) =>
                setValue(`entries.${index}.price`, Number(value), {
                  shouldDirty: true,
                })
              }
            />

            {!offer.isEvent && (
              <DatePicker
                {...register(`entries.${index}.bookingLimitDatetime`)}
                className={styles['input-booking-limit-datetime']}
                disabled={isReadOnly}
                error={errors.entries?.[index]?.bookingLimitDatetime?.message}
                label="Date limite de réservation"
                maxDate={computeEntryConstraints(entry).bookingLimitDatetimeMax}
                minDate={computeEntryConstraints(entry).bookingLimitDatetimeMin}
              />
            )}

            {isDateValid(entry.activationCodesExpirationDatetime) && (
              <DatePicker
                className={styles['input-activation-codes-expiration-datetime']}
                disabled
                error={
                  errors.entries?.[index]?.activationCodesExpirationDatetime
                    ?.message
                }
                label="Date d'expiration"
                name={`entries.${index}.activationCodesExpirationDatetime`}
                required
                value={entry.activationCodesExpirationDatetime ?? undefined}
              />
            )}

            {!offer.isEvent && (
              <QuantityInput
                className={styles['input-stock']}
                disabled={isReadOnly}
                error={errors.entries?.[index]?.quantity?.message}
                label="Stock"
                minimum={computeEntryConstraints(entry).quantityMin}
                onChange={(e) =>
                  setValue(
                    `entries.${index}.quantity`,
                    toNumberOrNull(e.target.value),
                    {
                      shouldDirty: true,
                    }
                  )
                }
                required
                value={entry.quantity}
              />
            )}

            {!offer.isEvent && mode === OFFER_WIZARD_MODE.EDITION && (
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
                    entry.remainingQuantity === 'unlimited'
                      ? 'Illimité'
                      : (entry.remainingQuantity ?? undefined)
                  }
                />

                <TextInput
                  {...register(`entries.${index}.bookingsQuantity`)}
                  className={styles['input-readonly']}
                  isOptional
                  label="Réservations"
                  readOnly
                  smallLabel
                  value={entry.bookingsQuantity ?? 0}
                />
              </>
            )}

            {!offer.isEvent && offer.isDigital && (
              <ListIconButton
                icon={fullCodeIcon}
                onClick={() => setActivationCodeEntryIndexToUpload(index)}
                readOnly={isReadOnly}
                ref={activationCodeButtonRef}
                tooltipContent="Ajouter des codes d'activation"
              />
            )}
            {fields.length > 1 && (
              <div className={styles['trash-button']}>
                <ListIconButton
                  icon={fullTrashIcon}
                  onClick={() => askForRemovalConfirmationOrRemove(index)}
                  tooltipContent="Supprimer ce tarif"
                />
              </div>
            )}
          </div>
        )
      })}

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
