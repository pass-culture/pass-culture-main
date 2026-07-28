import { yupResolver } from '@hookform/resolvers/yup'
import * as Dialog from '@radix-ui/react-dialog'
import { FormProvider, useForm } from 'react-hook-form'
import useSWR from 'swr'

import { api } from '@/apiClient/api'
import {
  type GetIndividualOfferWithAddressResponseModel,
  StocksOrderedBy,
} from '@/apiClient/v1'
import { GET_NEXT_STOCK_QUERY_KEY } from '@/commons/config/swrQueryKeys'
import { getPublicationHoursOptions } from '@/commons/utils/date'
import { MandatoryInfo } from '@/components/FormLayout/FormLayoutMandatoryInfo'
import { PublicationAndBookingFields } from '@/components/PublicationAndBookingFields/PublicationAndBookingFields'
import { ScrollToFirstHookFormErrorAfterSubmit } from '@/components/ScrollToFirstErrorAfterSubmit/ScrollToFirstErrorAfterSubmit'
import { Button } from '@/design-system/Button/Button'
import { ButtonColor, ButtonVariant } from '@/design-system/Button/types'
import { DialogBuilder } from '@/ui-kit/DialogBuilder/DialogBuilder'
import { Toggle } from '@/ui-kit/form/Toggle/Toggle'
import { Spinner } from '@/ui-kit/Spinner/Spinner'

import { getDefaultValuesFromOffer } from './getDefaultValuesFromOffer'
import styles from './OfferPublicationEditionForm.module.scss'
import type { EventPublicationEditionFormValues } from './types'
import { validationSchema } from './validationSchema'

export type OfferPublicationEditionFormProps = {
  offer: GetIndividualOfferWithAddressResponseModel
  onSubmit: (values: EventPublicationEditionFormValues) => void
}

export function OfferPublicationEditionForm({
  offer,
  onSubmit,
}: Readonly<OfferPublicationEditionFormProps>) {
  const getStocksQuery = useSWR(
    offer.id ? [GET_NEXT_STOCK_QUERY_KEY, offer.id] : null,
    ([, offerId]) =>
      api.getStocks({
        path: { offer_id: offerId },
        query: {
          stocks_limit_per_page: 1,
          page: 1,
          order_by_desc: false,
          order_by: StocksOrderedBy.BOOKING_LIMIT_DATETIME,
        },
      })
  )

  const publicationHoursOptions = getPublicationHoursOptions()
  const firstBookingLimitDatetime =
    getStocksQuery.data?.stocks[0]?.bookingLimitDatetime ?? ''

  const form = useForm<EventPublicationEditionFormValues>({
    defaultValues: getDefaultValuesFromOffer(offer, publicationHoursOptions),
    resolver: yupResolver<EventPublicationEditionFormValues, unknown, unknown>(
      validationSchema
    ),
    context: {
      firstBookingLimitDatetime,
    },
    mode: 'onBlur',
  })

  if (!getStocksQuery.data) {
    return <Spinner />
  }

  const isPaused = form.watch('isPaused')

  return (
    <FormProvider {...form}>
      <form
        onSubmit={form.handleSubmit(onSubmit)}
        className={styles['form']}
        noValidate
      >
        <ScrollToFirstHookFormErrorAfterSubmit />
        <MandatoryInfo />
        <div className={styles['form-content']}>
          <div className={styles['toggle']}>
            <Toggle
              label="Mettre en pause l’offre"
              labelPosition="right"
              isActiveByDefault={isPaused}
              handleClick={() => {
                if (isPaused && form.watch('publicationMode') === null) {
                  form.setValue('publicationMode', 'now')
                }
                form.setValue('isPaused', !isPaused)
              }}
            />
          </div>

          <PublicationAndBookingFields
            disabled={isPaused}
            maxDate={firstBookingLimitDatetime}
          />
        </div>

        <DialogBuilder.Footer>
          <div className={styles['actions']}>
            <Dialog.Close asChild>
              <Button
                variant={ButtonVariant.SECONDARY}
                color={ButtonColor.NEUTRAL}
                label="Annuler"
              />
            </Dialog.Close>
            <Button
              variant={ButtonVariant.PRIMARY}
              type="submit"
              label="Enregistrer"
            />
          </div>
        </DialogBuilder.Footer>
      </form>
    </FormProvider>
  )
}
