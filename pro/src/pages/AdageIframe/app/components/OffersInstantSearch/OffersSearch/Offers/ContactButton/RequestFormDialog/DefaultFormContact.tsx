import { useFormContext } from 'react-hook-form'

import { FormLayout } from 'components/FormLayout/FormLayout'
import { DatePicker } from 'ui-kit/formV2/DatePicker/DatePicker'
import { PhoneNumberInput } from 'ui-kit/formV2/PhoneNumberInput/PhoneNumberInput'
import { TextArea } from 'ui-kit/formV2/TextArea/TextArea'
import { TextInput } from 'ui-kit/formV2/TextInput/TextInput'

import { RequestFormValues } from './type'

export const DefaultFormContact = () => {
  // Get RHF context
  const {
    register,
    formState: { errors },
  } = useFormContext<RequestFormValues>()

  return (
    <>
      <FormLayout.Row mdSpaceAfter>
        <TextInput
          label="Email"
          {...register('teacherEmail')}
          disabled
          error={errors.teacherEmail?.message}
          required={true}
        />
      </FormLayout.Row>
      <FormLayout.Row>
        <PhoneNumberInput label="Téléphone" {...register('teacherPhone')} />
      </FormLayout.Row>
      <FormLayout.Row mdSpaceAfter>
        <DatePicker
          label="Date souhaitée"
          minDate={new Date()}
          {...register('offerDate')}
        />
      </FormLayout.Row>
      <FormLayout.Row mdSpaceAfter>
        <TextInput
          label="Nombre d'élèves"
          type="number"
          {...register('nbStudents')}
        />
      </FormLayout.Row>
      <FormLayout.Row mdSpaceAfter>
        <TextInput
          label="Nombre d'accompagnateurs"
          type="number"
          {...register('nbTeachers')}
        />
      </FormLayout.Row>
      <FormLayout.Row mdSpaceAfter>
        <TextArea
          label="Que souhaitez vous organiser ?"
          maxLength={1000}
          required={true}
          {...register('description')}
          description="Décrivez le projet que vous souhaiteriez co-construire avec l’acteur culturel (Ex : Je souhaite organiser une visite que vous proposez dans votre théâtre pour un projet pédagogique autour du théâtre et de l’expression corporelle avec ma classe de 30 élèves entre janvier et mars. Je suis joignable par téléphone ou par mail.)"
          error={errors.description?.message}
        />
      </FormLayout.Row>
    </>
  )
}
