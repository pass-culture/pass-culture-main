import classNames from 'classnames'
import { useRef, useState } from 'react'
import { useFieldArray, useFormContext } from 'react-hook-form'

import type {
  GetIndividualOfferWithAddressResponseModel,
  GetOfferStockResponseModel,
} from '@/apiClient/v1'
import { useIndividualOfferContext } from '@/commons/context/IndividualOfferContext/IndividualOfferContext'
import { OFFER_WIZARD_MODE } from '@/commons/core/Offers/constants'
import { isOfferDisabled } from '@/commons/core/Offers/utils/isOfferDisabled'
import { isOfferSynchronized } from '@/commons/core/Offers/utils/isOfferSynchronized'
import { isOfferSynchronizedViaAllocine } from '@/commons/core/Offers/utils/isOfferSynchronizedViaAllocine'
import { assertOrFrontendError } from '@/commons/errors/assertOrFrontendError'
import { isDateValid } from '@/commons/utils/date'
import { getDepartmentCode } from '@/commons/utils/getDepartmentCode'
import { toNumberOrNull } from '@/commons/utils/toNumberOrNull'
import { ActivationCodeFormDialog } from '@/components/IndividualOffer/StocksThing/ActivationCodeFormDialog/ActivationCodeFormDialog'
import { TextInput } from '@/design-system/TextInput/TextInput'
import fullCodeIcon from '@/icons/full-code.svg'
import fulleMoreIcon from '@/icons/full-more.svg'
import fullTrashIcon from '@/icons/full-trash.svg'
import { DialogStockThingDeleteConfirm } from '@/pages/IndividualOffer/components/DialogStockThingDeleteConfirm/DialogStockThingDeleteConfirm'
import { Button } from '@/ui-kit/Button/Button'
import { ButtonVariant } from '@/ui-kit/Button/types'
import { DatePicker } from '@/ui-kit/form/DatePicker/DatePicker'
import { PriceInput } from '@/ui-kit/form/PriceInput/PriceInput'
import { QuantityInput } from '@/ui-kit/form/QuantityInput/QuantityInput'
import { ListIconButton } from '@/ui-kit/ListIconButton/ListIconButton'

import {
  DEFAULT_PRICE_TABLE_ENTRY_LABEL_WHEN_SINGLE,
  PRICE_TABLE_ENTRY_MAX_LABEL_LENGTH,
} from '../../commons/constants'
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
  offerStocks: GetOfferStockResponseModel[]
}
export const PriceTableForm = ({
  isCaledonian,
  mode,
  offer,
  schemaValidationContext,
}: PriceTableFormProps) => {
  const activationCodeButtonRef = useRef<HTMLButtonElement>(null)

  const { hasPublishedOfferWithSameEan } = useIndividualOfferContext()

  const {
    control,
    getValues,
    watch,
    register,
    setValue,
    formState: { errors },
  } = useFormContext<PriceTableFormValues>()
  const { fields, append, remove, update } = useFieldArray({
    control,
    name: 'entries',
  })

  const [
    activationCodeEntryIndexToUpload,
    setActivationCodeEntryIndexToUpload,
  ] = useState<number | null>(null)
  const [entryIndexToConfirmAndRemove, setEntryIndexToConfirmAndRemove] =
    useState<number | null>(null)

  const areAllFieldsDisabled =
    isOfferDisabled(offer) || hasPublishedOfferWithSameEan
  const areAllFieldsDisabledButQuantity =
    !areAllFieldsDisabled &&
    isOfferSynchronized(offer) &&
    !isOfferSynchronizedViaAllocine(offer)
  const isEventOfferInEditionMode =
    offer.isEvent && mode === OFFER_WIZARD_MODE.EDITION

  const { computeEntryConstraints, nowAsDate } = makeFieldConstraints({
    offer,
    mode,
  })

  const firstEntry = watch('entries.0')
  const activationCodesExpirationDatetimeMin = firstEntry
    ? computeEntryConstraints(firstEntry).activationCodesExpirationDatetimeMin
    : null

  const addEntry = () => {
    const newEntry = PriceTableEntryValidationSchema.cast(
      { offerId: offer.id },
      { assert: false, context: schemaValidationContext }
    )

    append(newEntry, { shouldFocus: true })
  }

  const removeEntry = (indexToRemove: number) => {
    assertOrFrontendError(
      fields.length > 1,
      '`removeEntry` should not be called when there is only one entry.'
    )

    if (fields.length === 2) {
      const indexToKeep = indexToRemove === 0 ? 1 : 0

      setValue(
        `entries.${indexToKeep}.label`,
        DEFAULT_PRICE_TABLE_ENTRY_LABEL_WHEN_SINGLE
      )
    }

    remove(indexToRemove)
  }

  const resetEntry = (indexToReset: number) => {
    const initialEntry = {
      ...PriceTableEntryValidationSchema.cast(
        { offerId: offer.id },
        { assert: false, context: schemaValidationContext }
      ),
      label: DEFAULT_PRICE_TABLE_ENTRY_LABEL_WHEN_SINGLE,
    }

    update(indexToReset, initialEntry)
  }

  const askForRemovalConfirmationOrRemove = (indexToRemove: number) => {
    // If there is only one entry left, we reset it instead of removing it
    if (fields.length === 1) {
      resetEntry(indexToRemove)

      return
    }

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

        const hasActivationCodes =
          (watch(`entries.${index}.activationCodes`) || []).length > 0

        return (
          <div
            key={field.id}
            className={classNames(styles['row'], {
              [styles['event']]: offer.isEvent,
            })}
          >
            {offer.isEvent && (
              <div className={styles['input-label']}>
                <TextInput
                  {...register(`entries.${index}.label`)}
                  autoComplete="off"
                  disabled={
                    fields.length <= 1 ||
                    areAllFieldsDisabled ||
                    areAllFieldsDisabledButQuantity
                  }
                  error={errors.entries?.[index]?.label?.message}
                  label="Intitulé du tarif"
                  maxCharactersCount={PRICE_TABLE_ENTRY_MAX_LABEL_LENGTH}
                  description="Par exemple : catégorie 2, moins de 18 ans, pass 3 jours..."
                />
              </div>
            )}

            <div
              className={
                styles[offer.isDigital ? 'input-price--digital' : 'input-price']
              }
            >
              <PriceInput
                name="price"
                value={watch(`entries.${index}.price`) ?? ''}
                disabled={
                  areAllFieldsDisabled || areAllFieldsDisabledButQuantity
                }
                error={errors.entries?.[index]?.price?.message}
                label="Prix"
                currency={isCaledonian ? 'XPF' : 'EUR'}
                showFreeCheckbox={!offer.isDigital}
                onChange={(event) => {
                  setValue(
                    `entries.${index}.price`,
                    event.target.valueAsNumber,
                    {
                      shouldDirty: true,
                    }
                  )
                }}
              />
            </div>

            {!offer.isEvent && (
              <DatePicker
                {...register(`entries.${index}.bookingLimitDatetime`)}
                className={styles['input-booking-limit-datetime']}
                disabled={
                  areAllFieldsDisabled || areAllFieldsDisabledButQuantity
                }
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
              <div className={styles['input-stock']}>
                <QuantityInput
                  disabled={areAllFieldsDisabled || hasActivationCodes}
                  error={errors.entries?.[index]?.quantity?.message}
                  label="Stock"
                  min={computeEntryConstraints(entry).quantityMin}
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
              </div>
            )}

            {!offer.isEvent && mode === OFFER_WIZARD_MODE.EDITION && (
              <>
                <div className={styles['input-readonly']}>
                  <TextInput
                    label="Stock restant"
                    name="availableStock"
                    disabled
                    value={
                      entry.remainingQuantity === 'unlimited'
                        ? 'Illimité'
                        : (entry.remainingQuantity?.toString() ?? undefined)
                    }
                  />
                </div>

                <div className={styles['input-readonly']}>
                  <TextInput
                    name={`entries.${index}.bookingsQuantity`}
                    value={entry.bookingsQuantity?.toString() ?? '0'}
                    label="Réservations"
                    disabled
                  />
                </div>
              </>
            )}

            {!offer.isEvent &&
              offer.isDigital &&
              !areAllFieldsDisabled &&
              !areAllFieldsDisabledButQuantity && (
                <div className={styles['button-action']}>
                  <ListIconButton
                    icon={fullCodeIcon}
                    onClick={() => setActivationCodeEntryIndexToUpload(index)}
                    ref={activationCodeButtonRef}
                    tooltipContent="Ajouter des codes d'activation"
                  />
                </div>
              )}
            {
              // In EDITION mode, we don't allow removing/resetting prices for event offers
              !isEventOfferInEditionMode &&
                !areAllFieldsDisabled &&
                !areAllFieldsDisabledButQuantity && (
                  <div className={styles['button-action']}>
                    <ListIconButton
                      icon={fullTrashIcon}
                      onClick={() => askForRemovalConfirmationOrRemove(index)}
                      tooltipContent={
                        fields.length > 1
                          ? 'Supprimer ce tarif'
                          : 'Réinitialiser les valeurs de ce tarif'
                      }
                    />
                  </div>
                )
            }
          </div>
        )
      })}

      {offer.isEvent &&
        !areAllFieldsDisabled &&
        !areAllFieldsDisabledButQuantity && (
          <div className={styles['row']}>
            <Button
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
