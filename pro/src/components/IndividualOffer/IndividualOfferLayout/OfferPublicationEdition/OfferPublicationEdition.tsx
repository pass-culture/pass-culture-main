import { yupResolver } from '@hookform/resolvers/yup'
import * as Dialog from '@radix-ui/react-dialog'
import { isAfter } from 'date-fns'
import { FormProvider, useForm } from 'react-hook-form'

import { GetIndividualOfferWithAddressResponseModel } from 'apiClient/v1'
import { useActiveFeature } from 'commons/hooks/useActiveFeature'
import { MandatoryInfo } from 'components/FormLayout/FormLayoutMandatoryInfo'
import { getPublicationHoursOptions } from 'components/IndividualOffer/SummaryScreen/EventPublicationForm/EventPublicationForm'
import { EventPublicationFormValues } from 'components/IndividualOffer/SummaryScreen/EventPublicationForm/types'
import { validationSchema } from 'components/IndividualOffer/SummaryScreen/EventPublicationForm/validationSchema'
import { ScrollToFirstHookFormErrorAfterSubmit } from 'components/ScrollToFirstErrorAfterSubmit/ScrollToFirstErrorAfterSubmit'
import fullEditIcon from 'icons/full-edit.svg'
import { Button } from 'ui-kit/Button/Button'
import { ButtonVariant } from 'ui-kit/Button/types'
import { DialogBuilder } from 'ui-kit/DialogBuilder/DialogBuilder'
import { DatePicker } from 'ui-kit/formV2/DatePicker/DatePicker'
import { RadioGroup } from 'ui-kit/formV2/RadioGroup/RadioGroup'
import { Select } from 'ui-kit/formV2/Select/Select'

import styles from './OfferPublicationEdition.module.scss'

type OfferPublicationEditionProps = {
  offer: GetIndividualOfferWithAddressResponseModel
}

export function OfferPublicationEdition({
  offer,
}: OfferPublicationEditionProps) {
  const isRefactoFutureOfferEnabled = useActiveFeature(
    'WIP_REFACTO_FUTURE_OFFER'
  )

  const offerHadPublicationDateInTheFuture =
    offer.publicationDate && isAfter(offer.publicationDate, new Date())
  const offerHadBookabilityDateInTheFuture =
    offer.bookingAllowedDatetime &&
    isAfter(offer.bookingAllowedDatetime, new Date())
  const displayUpdatePublicationAndBookingDatesButton =
    isRefactoFutureOfferEnabled &&
    (offerHadPublicationDateInTheFuture || offerHadBookabilityDateInTheFuture)

  const form = useForm<EventPublicationFormValues>({
    defaultValues: {
      publicationMode: offer.publicationDatetime ? 'later' : 'now',
      bookingAllowedMode: offer.bookingAllowedDatetime ? 'later' : 'now',
    },
    resolver: yupResolver(validationSchema),
  })

  function onSubmit(values: EventPublicationFormValues) {
    console.log(values)
  }

  return (
    displayUpdatePublicationAndBookingDatesButton && (
      <DialogBuilder
        trigger={
          <Button variant={ButtonVariant.TERNARY} icon={fullEditIcon}>
            Modifier
          </Button>
        }
        title="Publication et réservation"
        variant="drawer"
      >
        <FormProvider {...form}>
          <form
            onSubmit={form.handleSubmit(onSubmit)}
            className={styles['form']}
          >
            <ScrollToFirstHookFormErrorAfterSubmit />
            <MandatoryInfo />
            <div className={styles['form-content']}>
              <RadioGroup
                className={styles['group']}
                legend="Quand votre offre doit-elle être publiée dans l’application ?"
                name="publicationMode"
                variant="detailed"
                group={[
                  { label: 'Publier maintenant', value: 'now', sizing: 'fill' },
                  {
                    label: 'Publier plus tard',
                    description:
                      'L’offre restera secrète pour le public jusqu’à sa publication.',
                    value: 'later',
                    sizing: 'fill',
                    collapsed: (
                      <div className={styles['inputs-row']}>
                        <DatePicker
                          label="Date"
                          minDate={new Date()}
                          className={styles['date-picker']}
                          required
                          {...form.register('publicationDate')}
                          error={form.formState.errors.publicationDate?.message}
                        />
                        <Select
                          label="Heure"
                          options={getPublicationHoursOptions()}
                          defaultOption={{ label: 'HH:MM', value: '' }}
                          className={styles['time-picker']}
                          required
                          {...form.register('publicationTime')}
                          error={form.formState.errors.publicationTime?.message}
                        />
                      </div>
                    ),
                  },
                ]}
                checkedOption={form.watch('publicationMode')}
                onChange={(event) => {
                  form.setValue(
                    'publicationMode',
                    event.target
                      .value as EventPublicationFormValues['publicationMode']
                  )
                }}
              />
              <RadioGroup
                className={styles['group']}
                legend="Quand votre offre pourra être réservable ?"
                name="bookingAllowedMode"
                variant="detailed"
                group={[
                  {
                    label: 'Rendre réservable dès la publication',
                    value: 'now',
                    sizing: 'fill',
                  },
                  {
                    label: 'Rendre réservable plus tard',
                    description:
                      'En activant cette option, vous permettez au public de visualiser l’entièreté de votre offre, de la mettre en favori et pouvoir la suivre mais sans qu’elle puisse être réservable.',
                    value: 'later',
                    sizing: 'fill',
                    collapsed: form.watch('bookingAllowedMode') === 'later' && (
                      <div className={styles['inputs-row']}>
                        <DatePicker
                          label="Date"
                          className={styles['date-picker']}
                          minDate={new Date()}
                          required
                          {...form.register('bookingAllowedDate')}
                          error={
                            form.formState.errors.bookingAllowedDate?.message
                          }
                        />
                        <Select
                          label="Heure"
                          options={getPublicationHoursOptions()}
                          defaultOption={{ label: 'HH:MM', value: '' }}
                          className={styles['time-picker']}
                          required
                          {...form.register('bookingAllowedTime')}
                          error={
                            form.formState.errors.bookingAllowedTime?.message
                          }
                        />
                      </div>
                    ),
                  },
                ]}
                checkedOption={form.watch('bookingAllowedMode')}
                onChange={(event) => {
                  form.setValue(
                    'bookingAllowedMode',
                    event.target
                      .value as EventPublicationFormValues['bookingAllowedMode']
                  )
                }}
              />
            </div>
            <DialogBuilder.Footer>
              <div className={styles['actions']}>
                <Dialog.Close asChild>
                  <Button variant={ButtonVariant.SECONDARY}>Annuler</Button>
                </Dialog.Close>
                <Button variant={ButtonVariant.PRIMARY} type="submit">
                  Valider
                </Button>
              </div>
            </DialogBuilder.Footer>
          </form>
        </FormProvider>
      </DialogBuilder>
    )
  )
}
