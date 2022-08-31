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
  externalTicketOfficeUrl: {
    label: /URL de votre site ou billetterie/,
    exact: true,
  },
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

export const findInputErrorForField = async fieldName => {
  return await screen.findByTestId(`input-error-field-${fieldName}`)
}

export const queryInputErrorForField = fieldName => {
  return screen.queryByTestId(`input-error-field-${fieldName}`)
}

export const setOfferValues = async values => {
  const checkboxes = [
    'audioDisabilityCompliant',
    'mentalDisabilityCompliant',
    'motorDisabilityCompliant',
    'visualDisabilityCompliant',
    'receiveNotificationEmails',
  ]
  const offerTypeRadio = ['isDuo']

  const setFormValueForField = async (field, value) => {
    let input
    const { label, exact } = fieldLabels[field]
    input = await screen.findByLabelText(label, { exact })

    if (checkboxes.includes(field)) {
      await userEvent.click(input)
    } else if (offerTypeRadio.includes(field)) {
      if (value) {
        await userEvent.click(input)
      } else {
        await userEvent.click(screen.getByLabelText('Aucune'))
      }
    } else if (input.type.includes('select')) {
      await userEvent.selectOptions(input, value)
    } else if (field === 'durationMinutes') {
      await userEvent.type(input, value)
    } else if (value === '') {
      await userEvent.clear(input)
    } else {
      await userEvent.type(input, value)
    }

    return input
  }

  const modifiedInputs = {}
  for (const fieldName in values) {
    if (fieldName === 'extraData') {
      modifiedInputs[fieldName] = await setOfferValues(values.extraData)
    } else {
      modifiedInputs[fieldName] = await setFormValueForField(
        fieldName,
        values[fieldName]
      )
    }
  }

  return Promise.resolve(modifiedInputs)
}

export const sidebarDisplayed = async () =>
  await screen.findByTestId('offer-preview-section')
