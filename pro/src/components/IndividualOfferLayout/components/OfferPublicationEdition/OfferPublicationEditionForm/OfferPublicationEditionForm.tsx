import { yupResolver } from '@hookform/resolvers/yup'
import * as Dialog from '@radix-ui/react-dialog'
import { FormProvider, useForm } from 'react-hook-form'

import type { GetIndividualOfferWithAddressResponseModel } from '@/apiClient/v1'
import { getPublicationHoursOptions } from '@/commons/utils/date'
import { MandatoryInfo } from '@/components/FormLayout/FormLayoutMandatoryInfo'
import { PublicationAndBookingFields } from '@/components/PublicationAndBookingFields/PublicationAndBookingFields'
import { ScrollToFirstHookFormErrorAfterSubmit } from '@/components/ScrollToFirstErrorAfterSubmit/ScrollToFirstErrorAfterSubmit'
import { Button } from '@/design-system/Button/Button'
import { ButtonColor, ButtonVariant } from '@/design-system/Button/types'
import { DialogBuilder } from '@/ui-kit/DialogBuilder/DialogBuilder'
import { Toggle } from '@/ui-kit/form/Toggle/Toggle'

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
  const publicationHoursOptions = getPublicationHoursOptions()

  const form = useForm<EventPublicationEditionFormValues>({
    defaultValues: getDefaultValuesFromOffer(offer, publicationHoursOptions),
    resolver: yupResolver<EventPublicationEditionFormValues, unknown, unknown>(
      validationSchema
    ),
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

          <PublicationAndBookingFields disabled={isPaused} />
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
