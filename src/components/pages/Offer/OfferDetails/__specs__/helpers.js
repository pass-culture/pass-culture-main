import { fireEvent, screen } from '@testing-library/react'

export const fieldLabels = {
  author: { label: 'Auteur', exact: true },
  bookingEmail: { label: 'Être notifié par email des réservations à :', exact: false },
  description: { label: 'Description', exact: false },
  durationMinutes: { label: 'Durée', exact: true },
  isbn: { label: 'ISBN', exact: true },
  isDuo: { label: 'Accepter les réservations "duo"', exact: false },
  isNational: { label: 'Rayonnement national', exact: true },
  name: { label: "Titre de l'offre", exact: true },
  musicSubType: { label: 'Sous genre', exact: true },
  musicType: { label: 'Genre musical', exact: true },
  offererId: { label: 'Structure', exact: true },
  performer: { label: 'Interprète', exact: true },
  receiveNotificationEmails: { label: 'Recevoir les emails de réservation', exact: true },
  showSubType: { label: 'Sous type', exact: true },
  showType: { label: 'Type de spectacle', exact: true },
  stageDirector: { label: 'Metteur en scène', exact: true },
  speaker: { label: 'Intervenant', exact: true },
  type: { label: 'Type', exact: true },
  url: { label: 'URL', exact: false },
  venueId: { label: 'Lieu', exact: true },
  visa: { label: 'Visa d’exploitation', exact: false },
  withdrawalDetails: { label: 'Informations de retrait', exact: false },
}

export const getOfferInputForField = async field => {
  const { label, exact } = fieldLabels[field]
  return await screen.findByLabelText(label, { exact })
}

export const setOfferValues = async values => {
  const checkboxes = ['bookingEmail', 'isDuo', 'receiveNotificationEmails']
  const setFormValueForField = async (field, value) => {
    let input
    const { label, exact } = fieldLabels[field]
    input = await screen.findByLabelText(label, { exact })
    if (checkboxes.includes(field)) {
      if (input.checked !== value) {
        fireEvent.click(input)
      }
    } else {
      fireEvent.change(input, { target: { value } })
    }

    return input
  }

  const modifiedInputs = {}
  for (const fieldName in values) {
    if (fieldName === 'extraData') {
      modifiedInputs[fieldName] = await setOfferValues(values.extraData)
    } else {
      modifiedInputs[fieldName] = await setFormValueForField(fieldName, values[fieldName])
    }
  }

  return Promise.resolve(modifiedInputs)
}
