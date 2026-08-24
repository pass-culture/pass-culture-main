import { yupResolver } from '@hookform/resolvers/yup'
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
import { Toggle } from '@/ui-kit/form/Toggle/Toggle'
import { Spinner } from '@/ui-kit/Spinner/Spinner'

export const OFFER_PUBLICATION_EDITION_FORM_ID =
  'offer-publication-edition-form'

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
          only_future_stocks: true,
        },
      })
  )

  const publicationHoursOptions = getPublicationHoursOptions()
  const nextBookingLimitDatetime =
    getStocksQuery.data?.stocks[0]?.bookingLimitDatetime ?? ''

  const form = useForm<EventPublicationEditionFormValues>({
    defaultValues: getDefaultValuesFromOffer(offer, publicationHoursOptions),
    resolver: yupResolver<EventPublicationEditionFormValues, unknown, unknown>(
      validationSchema
    ),
    context: {
      nextBookingLimitDatetime,
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
        id={OFFER_PUBLICATION_EDITION_FORM_ID}
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
            maxDate={nextBookingLimitDatetime}
          />
        </div>
      </form>
    </FormProvider>
  )
}
