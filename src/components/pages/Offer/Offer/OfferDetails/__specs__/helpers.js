import { screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'

export const fieldLabels = {
  author: { label: 'Auteur', exact: false },
  bookingEmail: { label: 'Email auquel envoyer les notifications :', exact: false },
  description: { label: 'Description', exact: false },
  durationMinutes: { label: 'Durée', exact: false },
  externalTicketOfficeUrl: { label: /URL de la billeterie/, exact: true },
  isbn: { label: 'ISBN', exact: false },
  isDuo: { label: 'Accepter les réservations "duo"', exact: false },
  audioDisabilityCompliant: { label: 'Handicap auditif', exact: true },
  mentalDisabilityCompliant: { label: 'Handicap mental', exact: true },
  motorDisabilityCompliant: { label: 'Handicap moteur', exact: true },
  visualDisabilityCompliant: { label: 'Handicap visuel', exact: true },
  noDisabilityCompliant: { label: 'Non accessible', exact: true },
  isNational: { label: 'Rayonnement national', exact: true },
  name: { label: "Titre de l'offre", exact: false },
  musicSubType: { label: 'Sous genre', exact: false },
  musicType: { label: 'Genre musical', exact: false },
  offererId: { label: 'Structure', exact: true },
  performer: { label: 'Interprète', exact: false },
  receiveNotificationEmails: { label: 'Être notifié par email des réservations', exact: true },
  showSubType: { label: 'Sous type', exact: false },
  showType: { label: 'Type de spectacle', exact: false },
  stageDirector: { label: 'Metteur en scène', exact: false },
  speaker: { label: 'Intervenant', exact: false },
  type: { label: 'Type', exact: true },
  url: { label: 'URL d’accès à l’offre', exact: false },
  venueId: { label: 'Lieu', exact: true },
  visa: { label: 'Visa d’exploitation', exact: false },
  withdrawalDetails: { label: 'Informations de retrait', exact: false },
}

export const getOfferInputForField = async fieldName => {
  const { label, exact } = fieldLabels[fieldName]
  return await screen.findByLabelText(label, { exact })
}

export const findInputErrorForField = fieldName => {
  return screen.findByTestId(`input-error-field-${fieldName}`)
}

export const queryInputErrorForField = fieldName => {
  return screen.queryByTestId(`input-error-field-${fieldName}`)
}

export const setOfferValues = async values => {
  const checkboxes = [
    'isDuo',
    'audioDisabilityCompliant',
    'mentalDisabilityCompliant',
    'motorDisabilityCompliant',
    'visualDisabilityCompliant',
    'receiveNotificationEmails',
  ]
  const selects = [
    'musicType',
    'musicSubType',
    'offererId',
    'showType',
    'showSubType',
    'type',
    'venueId',
  ]
  const setFormValueForField = (field, value) => {
    let input
    const { label, exact } = fieldLabels[field]
    input = screen.getByLabelText(label, { exact })
    if (checkboxes.includes(field)) {
      userEvent.click(input)
    } else if (selects.includes(field)) {
      userEvent.selectOptions(input, value)
    } else {
      userEvent.clear(input)
      userEvent.type(input, value)
    }

    return input
  }

  const modifiedInputs = {}
  for (const fieldName in values) {
    if (fieldName === 'extraData') {
      modifiedInputs[fieldName] = await setOfferValues(values.extraData)
    } else {
      modifiedInputs[fieldName] = setFormValueForField(fieldName, values[fieldName])
    }
  }

  return Promise.resolve(modifiedInputs)
}
