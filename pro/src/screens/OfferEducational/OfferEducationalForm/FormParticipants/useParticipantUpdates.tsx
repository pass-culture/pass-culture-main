import isEqual from 'lodash.isequal'
import { useEffect, useState } from 'react'

import { StudentLevels } from 'apiClient/v1'
import { IOfferEducationalFormValues } from 'core/OfferEducational'
import { buildStudentLevelsMapWithDefaultValue } from 'core/OfferEducational/utils/buildStudentLevelsMapWithDefaultValue'

const useParticipantUpdates = (
  values: IOfferEducationalFormValues['participants'],
  handleChange: (values: IOfferEducationalFormValues['participants']) => void
): void => {
  const [prevValue, setPrevValue] =
    useState<IOfferEducationalFormValues['participants']>(values)

  useEffect(() => {
    if (!isEqual(values, prevValue)) {
      const participantValues = Object.values(StudentLevels).map(
        studentLevel => values[studentLevel]
      )
      const areAllParticipantsSelected = participantValues.every(
        participant => participant === true
      )
      const wasAll = prevValue?.all ?? false
      const isAll = values.all
      const userSelectedAllParticipants = !wasAll && isAll
      const userDeselectedAllparticipants = wasAll && !isAll
      let newValues = { ...values }

      if (userSelectedAllParticipants) {
        newValues = {
          ...buildStudentLevelsMapWithDefaultValue(true),
          all: true,
        }
      } else if (userDeselectedAllparticipants) {
        newValues = {
          ...buildStudentLevelsMapWithDefaultValue(false),
          all: false,
        }
      } else if (!areAllParticipantsSelected) {
        newValues = {
          ...newValues,
          all: false,
        }
      } else if (areAllParticipantsSelected) {
        newValues = {
          ...newValues,
          all: true,
        }
      }

      if (!isEqual(values, newValues)) {
        handleChange(newValues)
      }

      setPrevValue(newValues)
    }
  }, [values, handleChange, prevValue])
}

export default useParticipantUpdates
