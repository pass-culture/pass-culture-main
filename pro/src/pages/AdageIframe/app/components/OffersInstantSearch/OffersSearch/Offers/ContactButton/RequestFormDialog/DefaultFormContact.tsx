import { useFormContext } from 'react-hook-form'

import { parseAndValidateFrenchPhoneNumber } from 'commons/core/shared/utils/parseAndValidateFrenchPhoneNumber'
import { FormLayout } from 'components/FormLayout/FormLayout'
import { DatePicker } from 'ui-kit/formV2/DatePicker/DatePicker'
import { PhoneNumberInput } from 'ui-kit/formV2/PhoneNumberInput/PhoneNumberInput'
import { TextArea } from 'ui-kit/formV2/TextArea/TextArea'
import { TextInput } from 'ui-kit/formV2/TextInput/TextInput'

import styles from './RequestFormDialog.module.scss'
import { RequestFormValues } from './type'

export const DefaultFormContact = () => {
  const {
    formState: { errors },
    register,
    setValue,
    watch,
  } = useFormContext<RequestFormValues>()

  return (
    <FormLayout>
      <FormLayout.Row mdSpaceAfter>
        <TextInput
          label="Email"
          {...register('teacherEmail')}
          error={errors.teacherEmail?.message}
          required
          disabled
        />
      </FormLayout.Row>
      <FormLayout.Row mdSpaceAfter>
        <PhoneNumberInput
          {...register('teacherPhone')}
          onBlur={(event) => {
            // This is because entries like "+33600110011invalid" are considered valid by libphonenumber-js,
            // We need to explicitely extract "+33600110011" that is in the .number property
            try {
              const phoneNumber = parseAndValidateFrenchPhoneNumber(
                event.target.value
              ).number
              setValue('teacherPhone', phoneNumber)
              // eslint-disable-next-line @typescript-eslint/no-unused-vars
            } catch (e) {
              // phone is considered invalid by the lib, so we does nothing here and let yup indicates the error
            }
          }}
          value={watch('teacherPhone')}
          onChange={(event) => setValue('teacherPhone', event.target.value)}
          error={errors.teacherPhone?.message}
          name="phoneNumber"
          label={'Téléphone'}
        />
      </FormLayout.Row>
      <FormLayout.Row mdSpaceAfter>
        <DatePicker
          className={styles['date-field-layout']}
          label="Date souhaitée"
          minDate={new Date()}
          error={errors.offerDate?.message}
          {...register('offerDate')}
        />
      </FormLayout.Row>
      <FormLayout.Row mdSpaceAfter>
        <TextInput
          label="Nombre d'élèves"
          {...register('nbStudents')}
          error={errors.nbStudents?.message}
          type="number"
        />
      </FormLayout.Row>
      <FormLayout.Row mdSpaceAfter>
        <TextInput
          label="Nombre d'accompagnateurs"
          {...register('nbTeachers')}
          error={errors.nbTeachers?.message}
          type="number"
        />
      </FormLayout.Row>
      <FormLayout.Row mdSpaceAfter>
        <TextArea
          name="description"
          value={watch('description')}
          onChange={(e) => setValue('description', e.target.value)}
          label="Que souhaitez vous organiser ?"
          maxLength={1000}
          description="Décrivez le projet que vous souhaiteriez co-construire avec l’acteur culturel (Ex : Je souhaite organiser une visite que vous proposez dans votre théâtre pour un projet pédagogique autour du théâtre et de l’expression corporelle avec ma classe de 30 élèves entre janvier et mars. Je suis joignable par téléphone ou par mail.)"
          required
          error={errors.description?.message}
        />
      </FormLayout.Row>
    </FormLayout>
  )
}
