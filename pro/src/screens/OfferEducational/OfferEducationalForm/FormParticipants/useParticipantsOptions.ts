import { StudentLevels } from 'apiClient/v1'
import { OfferEducationalFormValues } from 'core/OfferEducational'
import { buildStudentLevelsMapWithDefaultValue } from 'core/OfferEducational/utils/buildStudentLevelsMapWithDefaultValue'

export const ALL_STUDENTS_LABEL = 'Tout sélectionner'

const useParticipantsOptions = (
  values: OfferEducationalFormValues['participants'],
  setFieldValue: (
    field: string,
    value: any,
    shouldValidate?: boolean | undefined
  ) => void,
  isTemplate: boolean = false
) => {
  const canToggleAllParticipants = isTemplate

  const handleParticipantsAllChange = (
    event: React.ChangeEvent<HTMLInputElement>
  ) => {
    if (event.target.checked) {
      setFieldValue('participants', {
        ...buildStudentLevelsMapWithDefaultValue(true),
        all: true,
      })
    } else {
      setFieldValue('participants', {
        ...buildStudentLevelsMapWithDefaultValue(false),
        all: false,
      })
    }
  }
  const handleParticipantsChange = (
    event: React.ChangeEvent<HTMLInputElement>
  ) => {
    if (!event.target.checked && canToggleAllParticipants) {
      setFieldValue('participants.all', false)
    }
  }

  return [
    ...(canToggleAllParticipants
      ? [
          {
            label: ALL_STUDENTS_LABEL,
            name: 'participants.all',
            onChange: handleParticipantsAllChange,
          },
        ]
      : []),
    ...Object.values(StudentLevels).map(studentLevel => ({
      label: studentLevel,
      name: `participants.${studentLevel}`,
      onChange: handleParticipantsChange,
    })),
  ]
}
export default useParticipantsOptions
