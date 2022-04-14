import { fireEvent } from '@testing-library/dom'
import { screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'

export const fieldLabels = {
  author: { label: 'Auteur', exact: false },
  bookingEmail: {
    label: 'Email auquel envoyer les notifications :',
    exact: false,
  },
  description: { label: 'Description', exact: false },
  durationMinutes: { label: 'Durée', exact: false },
  externalTicketOfficeUrl: { label: /URL de redirection externe/, exact: true },
  isbn: { label: 'ISBN', exact: false },
  isDuo: { label: 'Accepter les réservations "duo"', exact: false },
  audioDisabilityCompliant: { label: 'Auditif', exact: true },
  mentalDisabilityCompliant: { label: 'Psychique ou cognitif', exact: true },
  motorDisabilityCompliant: { label: 'Moteur', exact: true },
  visualDisabilityCompliant: { label: 'Visuel', exact: true },
  noDisabilityCompliant: { label: 'Non accessible', exact: true },
  isNational: { label: 'Rayonnement national', exact: true },
  name: { label: "Titre de l'offre", exact: false },
  musicType: { label: 'Genre musical', exact: false },
  musicSubType: { label: 'Sous genre', exact: false },
  offererId: { label: 'Structure', exact: true },
  performer: { label: 'Interprète', exact: false },
  receiveNotificationEmails: {
    label: 'Être notifié par email des réservations',
    exact: true,
  },
  showSubType: { label: 'Sous type', exact: false },
  showType: { label: 'Type de spectacle', exact: false },
  stageDirector: { label: 'Metteur en scène', exact: false },
  speaker: { label: 'Intervenant', exact: false },
  categoryId: { label: 'Catégorie', exact: true },
  subcategoryId: { label: 'Sous-catégorie', exact: true },
  url: { label: 'URL d’accès à l’offre', exact: false },
  venueId: { label: 'Lieu', exact: true },
  visa: { label: 'Visa d’exploitation', exact: false },
  withdrawalDetails: { label: 'Informations de retrait', exact: false },
  withdrawalType: { label: 'Évènement sans billet', exact: false },
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

export const setOfferValues = values => {
  const checkboxes = [
    'audioDisabilityCompliant',
    'mentalDisabilityCompliant',
    'motorDisabilityCompliant',
    'visualDisabilityCompliant',
    'receiveNotificationEmails',
  ]
  const offerTypeRadio = ['isDuo']

  const setFormValueForField = (field, value) => {
    let input
    const { label, exact } = fieldLabels[field]
    input = screen.getByLabelText(label, { exact })

    if (checkboxes.includes(field)) {
      userEvent.click(input)
    } else if (offerTypeRadio.includes(field)) {
      if (value) {
        userEvent.click(input)
      } else {
        userEvent.click(screen.getByLabelText('Aucune'))
      }
    } else if (field === 'durationMinutes') {
      userEvent.type(input, value)
    } else {
      fireEvent.change(input, { target: { value } })
    }

    return input
  }

  const modifiedInputs = {}
  for (const fieldName in values) {
    if (fieldName === 'extraData') {
      modifiedInputs[fieldName] = setOfferValues(values.extraData)
    } else {
      modifiedInputs[fieldName] = setFormValueForField(
        fieldName,
        values[fieldName]
      )
    }
  }

  return Promise.resolve(modifiedInputs)
}

export const sidebarDisplayed = async () => {
  await screen.findByText('Ajouter une image')
  return Promise.resolve(null)
}
