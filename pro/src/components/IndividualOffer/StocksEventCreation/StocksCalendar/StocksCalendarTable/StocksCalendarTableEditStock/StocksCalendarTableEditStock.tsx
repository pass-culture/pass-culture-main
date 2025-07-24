import { yupResolver } from '@hookform/resolvers/yup'
import * as Dialog from '@radix-ui/react-dialog'
import { useId } from 'react'
import { FormProvider, useForm } from 'react-hook-form'

import {
  EventStockUpdateBodyModel,
  GetIndividualOfferResponseModel,
  GetOfferStockResponseModel,
} from 'apiClient/v1'
import { MandatoryInfo } from 'components/FormLayout/FormLayoutMandatoryInfo'
import { getPriceCategoryOptions } from 'components/IndividualOffer/PriceCategoriesScreen/form/getPriceCategoryOptions'
import { Button } from 'ui-kit/Button/Button'
import { ButtonVariant } from 'ui-kit/Button/types'
import { DialogBuilder } from 'ui-kit/DialogBuilder/DialogBuilder'
import { DatePicker } from 'ui-kit/form/DatePicker/DatePicker'
import { QuantityInput } from 'ui-kit/form/QuantityInput/QuantityInput'
import { Select } from 'ui-kit/form/Select/Select'
import { TimePicker } from 'ui-kit/form/TimePicker/TimePicker'

import styles from './StocksCalendarTableEditStock.module.scss'
import {
  getStockFormDefaultValues,
  serializeStockFormValuesForUpdate,
} from './utils'
import { validationSchema } from './validationSchema'

export type EditStockFormValues = {
  date: string
  time: string
  priceCategory: string
  bookingLimitDate: string
  quantity?: number
}

export type StocksCalendarTableEditStockProps = {
  stock: GetOfferStockResponseModel
  departmentCode: string
  priceCategories: GetIndividualOfferResponseModel['priceCategories']
  onUpdateStock: (body: EventStockUpdateBodyModel) => void
}

export function StocksCalendarTableEditStock({
  stock,
  departmentCode,
  priceCategories,
  onUpdateStock,
}: StocksCalendarTableEditStockProps) {
  const form = useForm<EditStockFormValues>({
    defaultValues: getStockFormDefaultValues(stock, departmentCode),
    resolver: yupResolver(validationSchema),
  })

  function onSubmit() {
    onUpdateStock(
      serializeStockFormValuesForUpdate(stock.id, form, departmentCode)
    )
  }

  const descriptionId = useId()

  const quantity = form.watch(`quantity`)

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
            />
            <TimePicker
              {...form.register('time')}
              className={styles['time']}
              label="Horaire"
              required
              error={form.formState.errors.time?.message}
            />
          </div>
          <h2 className={styles['title']}>Places et tarifs</h2>
          <div className={styles['row']}>
            <div className={styles['price-category-row']}>
              <QuantityInput
                minimum={0}
                error={form.formState.errors.quantity?.message}
                label="Nombre de places"
                value={quantity}
                onChange={(e) => {
                  const value = e.target.value
                  form.setValue(
                    `quantity`,
                    value === '' ? undefined : Number(value)
                  )
                }}
              />
            </div>
            <Select
              label="Tarif"
              {...form.register('priceCategory')}
              options={getPriceCategoryOptions(priceCategories)}
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
              <Button type="button" variant={ButtonVariant.SECONDARY}>
                Annuler
              </Button>
            </Dialog.Close>
            <Button type="submit">Valider</Button>
          </div>
        </DialogBuilder.Footer>
      </form>
    </FormProvider>
  )
}
