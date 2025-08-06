import { yupResolver } from '@hookform/resolvers/yup'
import * as Dialog from '@radix-ui/react-dialog'
import { format, isAfter } from 'date-fns'
import { FormProvider, useForm } from 'react-hook-form'

import { GetIndividualOfferWithAddressResponseModel } from '@/apiClient//v1'
import { SelectOption } from '@/commons/custom_types/form'
import { FORMAT_HH_mm, formatShortDateForInput } from '@/commons/utils/date'
import { getLocalDepartementDateTimeFromUtc } from '@/commons/utils/timezone'
import { MandatoryInfo } from '@/components/FormLayout/FormLayoutMandatoryInfo'
import { ScrollToFirstHookFormErrorAfterSubmit } from '@/components/ScrollToFirstErrorAfterSubmit/ScrollToFirstErrorAfterSubmit'
import { RadioButtonGroup } from '@/design-system/RadioButtonGroup/RadioButtonGroup'
import { getPublicationHoursOptions } from '@/pages/IndividualOfferSummary/IndividualOfferSummary/components/EventPublicationForm/EventPublicationForm'
import { EventPublicationFormValues } from '@/pages/IndividualOfferSummary/IndividualOfferSummary/components/EventPublicationForm/types'
import { Button } from '@/ui-kit/Button/Button'
import { ButtonVariant } from '@/ui-kit/Button/types'
import { DialogBuilder } from '@/ui-kit/DialogBuilder/DialogBuilder'
import { DatePicker } from '@/ui-kit/form/DatePicker/DatePicker'
import { Select } from '@/ui-kit/form/Select/Select'
import { Toggle } from '@/ui-kit/Toggle/Toggle'

import styles from './OfferPublicationEditionForm.module.scss'
import { EventPublicationEditionFormValues } from './types'
import { validationSchema } from './validationSchema'

export type OfferPublicationEditionFormProps = {
  offer: GetIndividualOfferWithAddressResponseModel
  onSubmit: (values: EventPublicationEditionFormValues) => void
}

function getDefaultValuesFromOffer(
  offer: GetIndividualOfferWithAddressResponseModel,
  publicationHoursOptions: SelectOption[]
) {
  let publicationMode: EventPublicationEditionFormValues['publicationMode'] =
    null
  if (
    offer.publicationDatetime &&
    isAfter(offer.publicationDatetime, new Date())
  ) {
    publicationMode = 'later'
  } else {
    publicationMode = 'now'
  }

  const publicationTime = offer.publicationDatetime
    ? format(
        getLocalDepartementDateTimeFromUtc(offer.publicationDatetime),
        FORMAT_HH_mm
      )
    : undefined

  return {
    publicationMode,
    publicationDate: offer.publicationDatetime
      ? formatShortDateForInput(
          getLocalDepartementDateTimeFromUtc(offer.publicationDatetime)
        )
      : undefined,
    //  If the publication date was set by the backend to a date outside of allowed times, reset the field
    publicationTime:
      publicationTime &&
      publicationHoursOptions.map((op) => op.value).includes(publicationTime)
        ? publicationTime
        : undefined,
    bookingAllowedMode:
      offer.bookingAllowedDatetime &&
      isAfter(offer.bookingAllowedDatetime, new Date())
        ? 'later'
        : 'now',
    bookingAllowedDate: offer.bookingAllowedDatetime
      ? formatShortDateForInput(
          getLocalDepartementDateTimeFromUtc(offer.bookingAllowedDatetime)
        )
      : undefined,
    bookingAllowedTime: offer.bookingAllowedDatetime
      ? format(
          getLocalDepartementDateTimeFromUtc(offer.bookingAllowedDatetime),
          FORMAT_HH_mm
        )
      : undefined,
    isPaused: offer.publicationDatetime === null,
  } satisfies EventPublicationEditionFormValues
}

export function OfferPublicationEditionForm({
  offer,
  onSubmit,
}: Readonly<OfferPublicationEditionFormProps>) {
  const publicationHoursOptions = getPublicationHoursOptions()

  const form = useForm<EventPublicationEditionFormValues>({
    defaultValues: getDefaultValuesFromOffer(offer, publicationHoursOptions),
    resolver: yupResolver(validationSchema),
    mode: 'onBlur',
  })

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
          <RadioButtonGroup
            className={styles['group']}
            label="Quand votre offre doit-elle être publiée dans l’application ?"
            name="publicationMode"
            variant="detailed"
            disabled={isPaused}
            options={[
              { label: 'Publier maintenant', value: 'now' },
              {
                label: 'Publier plus tard',
                description:
                  'L’offre restera secrète pour le public jusqu’à sa publication.',
                value: 'later',
                collapsed: (
                  <div className={styles['inputs-row']}>
                    <DatePicker
                      label="Date"
                      minDate={new Date()}
                      className={styles['date-picker']}
                      disabled={isPaused}
                      required
                      {...form.register('publicationDate')}
                      onBlur={async (e) => {
                        await form.register('publicationDate').onBlur(e)
                        await form.trigger('publicationTime')
                      }}
                      error={form.formState.errors.publicationDate?.message}
                    />
                    <Select
                      label="Heure"
                      options={publicationHoursOptions}
                      defaultOption={{ label: 'HH:MM', value: '' }}
                      className={styles['time-picker']}
                      disabled={isPaused}
                      required
                      {...form.register('publicationTime')}
                      error={form.formState.errors.publicationTime?.message}
                    />
                  </div>
                ),
              },
            ]}
            checkedOption={
              isPaused ? undefined : form.watch('publicationMode') || undefined
            }
            onChange={(event) => {
              form.setValue(
                'publicationMode',
                event.target
                  .value as EventPublicationFormValues['publicationMode']
              )
            }}
          />
          <RadioButtonGroup
            className={styles['group']}
            label="Quand votre offre pourra être réservable ?"
            name="bookingAllowedMode"
            variant="detailed"
            disabled={isPaused}
            options={[
              {
                label: 'Rendre réservable dès la publication',
                value: 'now',
              },
              {
                label: 'Rendre réservable plus tard',
                description:
                  'En activant cette option, vous permettez au public de visualiser l’entièreté de votre offre, de la mettre en favori et pouvoir la suivre mais sans qu’elle puisse être réservable.',
                value: 'later',
                collapsed: form.watch('bookingAllowedMode') === 'later' && (
                  <div className={styles['inputs-row']}>
                    <DatePicker
                      label="Date"
                      className={styles['date-picker']}
                      minDate={new Date()}
                      disabled={isPaused}
                      required
                      {...form.register('bookingAllowedDate')}
                      onBlur={async (e) => {
                        await form.register('bookingAllowedDate').onBlur(e)
                        await form.trigger('bookingAllowedDate')
                      }}
                      error={form.formState.errors.bookingAllowedDate?.message}
                    />
                    <Select
                      label="Heure"
                      options={publicationHoursOptions}
                      defaultOption={{ label: 'HH:MM', value: '' }}
                      className={styles['time-picker']}
                      disabled={isPaused}
                      required
                      {...form.register('bookingAllowedTime')}
                      error={form.formState.errors.bookingAllowedTime?.message}
                    />
                  </div>
                ),
              },
            ]}
            checkedOption={
              isPaused
                ? undefined
                : form.watch('bookingAllowedMode') || undefined
            }
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
              Enregistrer
            </Button>
          </div>
        </DialogBuilder.Footer>
      </form>
    </FormProvider>
  )
}
