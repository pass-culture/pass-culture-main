import { StudentLevels } from 'apiClient/v1'
import { IOfferEducationalFormValues } from 'core/OfferEducational'
import { buildStudentLevelsMapWithDefaultValue } from 'core/OfferEducational/utils/buildStudentLevelsMapWithDefaultValue'

export const ALL_STUDENTS_LABEL = 'Tout sélectionner'

const getStudentLevelLabel = (studentLevel: StudentLevels) => {
  switch (studentLevel) {
    case StudentLevels.COLL_GE_6E:
    case StudentLevels.COLL_GE_5E:
      return `${studentLevel} : à partir de septembre 2023`
    default:
      return studentLevel
  }
}
const useParticipantsOptions = (
  values: IOfferEducationalFormValues['participants'],
  setFieldValue: (
    field: string,
    value: any,
    shouldValidate?: boolean | undefined
  ) => void
) => {
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
    if (!event.target.checked) {
      setFieldValue('participants.all', false)
    }
  }
  return [
    {
      label: ALL_STUDENTS_LABEL,
      name: 'participants.all',
      onChange: handleParticipantsAllChange,
    },
    ...Object.values(StudentLevels).map(studentLevel => ({
      label: getStudentLevelLabel(studentLevel),
      name: `participants.${studentLevel}`,
      onChange: handleParticipantsChange,
    })),
  ]
}
export default useParticipantsOptions
