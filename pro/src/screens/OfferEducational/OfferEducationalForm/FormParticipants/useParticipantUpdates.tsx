import isEqual from 'lodash.isequal'
import { useEffect, useState } from 'react'

import { IOfferEducationalFormValues } from 'core/OfferEducational'

const useParticipantUpdates = (
  values: IOfferEducationalFormValues['participants'],
  handleChange: (values: IOfferEducationalFormValues['participants']) => void
): void => {
  const [prevValue, setPrevValue] =
    useState<IOfferEducationalFormValues['participants']>(values)

  useEffect(() => {
    if (!isEqual(values, prevValue)) {
      const participantValues = [
        values.quatrieme,
        values.troisieme,
        values.seconde,
        values.premiere,
        values.terminale,
        values.CAPAnnee1,
        values.CAPAnnee2,
      ]
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
          ...newValues,
          quatrieme: true,
          troisieme: true,
          seconde: true,
          premiere: true,
          terminale: true,
          CAPAnnee1: true,
          CAPAnnee2: true,
        }
      } else if (userDeselectedAllparticipants) {
        newValues = {
          ...newValues,
          quatrieme: false,
          troisieme: false,
          seconde: false,
          premiere: false,
          terminale: false,
          CAPAnnee1: false,
          CAPAnnee2: false,
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
