import { yupResolver } from '@hookform/resolvers/yup'
import * as Dialog from '@radix-ui/react-dialog'
import { useId } from 'react'
import { FormProvider, useForm } from 'react-hook-form'

import type {
  EventStockUpdateBodyModel,
  GetIndividualOfferResponseModel,
  GetOfferStockResponseModel,
} from '@/apiClient/v1'
import { isOfferAllocineSynchronized } from '@/commons/core/Offers/utils/typology'
import { useIsCaledonian } from '@/commons/hooks/useIsCaledonian'
import { MandatoryInfo } from '@/components/FormLayout/FormLayoutMandatoryInfo'
import { Button } from '@/design-system/Button/Button'
import { ButtonColor, ButtonVariant } from '@/design-system/Button/types'
import { getPriceCategoryOptions } from '@/pages/IndividualOffer/commons/getPriceCategoryOptions'
import { DialogBuilder } from '@/ui-kit/DialogBuilder/DialogBuilder'
import { DatePicker } from '@/ui-kit/form/DatePicker/DatePicker'
import { QuantityInput } from '@/ui-kit/form/QuantityInput/QuantityInput'
import { Select } from '@/ui-kit/form/Select/Select'
import { TimePicker } from '@/ui-kit/form/TimePicker/TimePicker'

import styles from './StocksCalendarTableEditStock.module.scss'
import {
  getStockFormDefaultValues,
  serializeStockFormValuesForUpdate,
} from './serializers'
import { validationSchema } from './validationSchema'

export type EditStockFormValues = {
  date: string
  time: string
  priceCategory: string
  bookingLimitDate: string
  remainingQuantity?: number
}

export type StocksCalendarTableEditStockProps = {
  stock: GetOfferStockResponseModel
  departmentCode: string
  priceCategories: GetIndividualOfferResponseModel['priceCategories']
  onUpdateStock: (body: EventStockUpdateBodyModel) => void
  offer: GetIndividualOfferResponseModel
}

export function StocksCalendarTableEditStock({
  offer,
  stock,
  departmentCode,
  priceCategories,
  onUpdateStock,
}: StocksCalendarTableEditStockProps) {
  const isCaledonian = useIsCaledonian()

  const form = useForm<EditStockFormValues>({
    defaultValues: getStockFormDefaultValues(stock, departmentCode),
    resolver: yupResolver(validationSchema),
  })

  const isAllocineSynchro = isOfferAllocineSynchronized(offer)

  const formValues = form.watch()

  function onSubmit() {
    onUpdateStock(
      serializeStockFormValuesForUpdate(stock, formValues, departmentCode)
    )
  }

  const descriptionId = useId()

  const remainingQuantity = form.watch(`remainingQuantity`)

  return (
    <FormProvider {...form}>
      <MandatoryInfo />
      <form
        className={styles['form']}
        onSubmit={form.handleSubmit(onSubmit)}
        noValidate
      >
        <div className={styles['content']}>
          <div className={styles['row']}>
            <DatePicker
              {...form.register('date')}
              className={styles['date']}
              label="Date"
              required
              error={form.formState.errors.date?.message}
              minDate={new Date()}
              disabled={isAllocineSynchro}
            />
            <TimePicker
              {...form.register('time')}
              className={styles['time']}
              label="Horaire"
              required
              error={form.formState.errors.time?.message}
              disabled={isAllocineSynchro}
            />
          </div>
          <h2 className={styles['title']}>Places et tarifs</h2>
          <div className={styles['row']}>
            <div className={styles['price-category-row']}>
              <QuantityInput
                min={0}
                error={form.formState.errors.remainingQuantity?.message}
                label="Places restantes"
                value={remainingQuantity}
                onChange={(e) => {
                  const value = e.target.value
                  form.setValue(
                    `remainingQuantity`,
                    value === '' ? undefined : Number(value)
                  )
                }}
              />
            </div>
            <Select
              label="Tarif"
              {...form.register('priceCategory')}
              options={getPriceCategoryOptions(priceCategories, isCaledonian)}
              required
              className={styles['price-category']}
            />
          </div>
          <div>
            <h2 className={styles['title']}>Date limite de réservation</h2>
            <p className={styles['description']} id={descriptionId}>
              C’est la date à laquelle les jeunes ne pourront plus réserver
              votre offre
            </p>
            <DatePicker
              {...form.register('bookingLimitDate')}
              label="Date"
              className={styles['date']}
              required
              aria-describedBy={descriptionId}
              error={form.formState.errors.bookingLimitDate?.message}
            />
          </div>
        </div>
        <DialogBuilder.Footer>
          <div className={styles['footer']}>
            <Dialog.Close asChild>
              <Button
                type="button"
                variant={ButtonVariant.SECONDARY}
                color={ButtonColor.NEUTRAL}
                label="Annuler"
              />
            </Dialog.Close>
            <Button type="submit" label="Valider" />
          </div>
        </DialogBuilder.Footer>
      </form>
    </FormProvider>
  )
}
