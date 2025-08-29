import { useFormContext } from 'react-hook-form'

import { FormLayout } from '@/components/FormLayout/FormLayout'
import { RadioButtonGroup } from '@/design-system/RadioButtonGroup/RadioButtonGroup'
import { getPublicationHoursOptions } from '@/pages/IndividualOfferSummary/IndividualOfferSummary/components/EventPublicationForm/EventPublicationForm'
import { DatePicker } from '@/ui-kit/form/DatePicker/DatePicker'
import { Select } from '@/ui-kit/form/Select/Select'

import type { IndividualOfferPracticalInfosFormValues } from '../../../commons/types'
import styles from './IndividualOfferPracticalInfosFormPublication.module.scss'

export function IndividualOfferPracticalInfosFormPublication({
  isFormDisabled,
}: {
  isFormDisabled: boolean
}) {
  const form = useFormContext<IndividualOfferPracticalInfosFormValues>()

  return (
    <FormLayout.Row mdSpaceAfter>
      <RadioButtonGroup
        label="Quand votre offre pourra-t-elle être réservable&nbsp;?"
        variant="detailed"
        disabled={isFormDisabled}
        options={[
          { label: 'Rendre réservable dès la publication', value: 'now' },
          {
            label: 'Rendre réservable plus tard',
            value: 'later',
            collapsed: form.watch('bookingAllowedMode') === 'later' && (
              <div className={styles['inputs-row']}>
                <DatePicker
                  label="Date"
                  disabled={isFormDisabled}
                  className={styles['date-picker']}
                  minDate={new Date()}
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
                  disabled={isFormDisabled}
                  options={getPublicationHoursOptions()}
                  defaultOption={{ label: 'HH:MM', value: '' }}
                  className={styles['time-picker']}
                  required
                  {...form.register('bookingAllowedTime')}
                  error={form.formState.errors.bookingAllowedTime?.message}
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
              .value as IndividualOfferPracticalInfosFormValues['bookingAllowedMode']
          )
        }}
        name="bookingAllowedMode"
      />
    </FormLayout.Row>
  )
}
