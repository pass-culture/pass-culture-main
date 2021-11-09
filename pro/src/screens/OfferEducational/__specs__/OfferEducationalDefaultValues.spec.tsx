import '@testing-library/jest-dom'
import { screen, render } from '@testing-library/react'
import { createBrowserHistory } from 'history'
import React from 'react'
import { Router } from 'react-router'

import { getCategoriesSelect, getSubcategoriesSelect } from '../__tests-utils__/eacOfferCreationUtils'
import setDefaultProps from '../__tests-utils__/setDefaultProps'
import OfferEducational, { IOfferEducationalProps } from '../OfferEducational'
import { accessibilityOptions } from '../OfferEducationalForm/FormAccessibility/accessibilityOptions'
import { participantsOptions } from '../OfferEducationalForm/FormParticipants/participantsOptions'


const renderEACOfferCreation = (props: IOfferEducationalProps, overrideProps?: Partial<IOfferEducationalProps>) => {
  const history = createBrowserHistory()
  return render(
    <Router history={history}>
      <OfferEducational
        {...props}
        {...overrideProps}
      />
    </Router>
  )
}

describe('screens | OfferEducational', () => {
  let props: IOfferEducationalProps

  beforeEach(() => {
    props = setDefaultProps()
  })
  
  it('should have no initial values', () => {
    renderEACOfferCreation(props, { educationalCategories: [], educationalSubcategories: [] })

    const categoriesSelect = getCategoriesSelect()
    expect(categoriesSelect.value).toBe('')

    const subCategoriesSelect = getSubcategoriesSelect()
    expect(subCategoriesSelect.value).toBe('')

    const titleInput = screen.getByLabelText("Titre de l'offre") as HTMLInputElement
    expect(titleInput.value).toBe('')

    const descriptionTextArea = screen.getByLabelText('Description') as HTMLTextAreaElement
    expect(descriptionTextArea.value).toBe('')

    const offererSelect = screen.getByLabelText('Structure') as HTMLSelectElement
    expect(offererSelect.value).toBe('')

    const venueSelect = screen.getByLabelText('Lieu qui percevra le remboursement') as HTMLSelectElement
    expect(venueSelect.value).toBe('')

    const offerVenueRadio1 = screen.getByLabelText('Dans votre établissement') as HTMLInputElement
    const offerVenueRadio2 = screen.getByLabelText("Dans l'établissement scolaire") as HTMLInputElement
    const offerVenueRadio3 = screen.getByLabelText('Autre') as HTMLInputElement
    [offerVenueRadio1, offerVenueRadio2, offerVenueRadio3].forEach(radio => {
      expect(radio.checked).toBe(false)
    })

    participantsOptions.forEach(participantsOption => {
      const participantsCheckbox = screen.getByLabelText(participantsOption.label) as HTMLInputElement
      expect(participantsCheckbox.checked).toBe(false)
    })
    
    accessibilityOptions.forEach(accessibilityOption => {
      const accessibilityCheckbox = screen.getByLabelText(accessibilityOption.label) as HTMLInputElement
      expect(accessibilityCheckbox.checked).toBe(false)
    })

    const phoneInput = screen.getByLabelText('Téléphone') as HTMLInputElement
    expect(phoneInput.value).toBe('')

    const emailInput = screen.getByLabelText('Email') as HTMLInputElement
    expect(emailInput.value).toBe('')

    const notificationsCheckbox = screen.getByLabelText('Être notifié par email des réservations') as HTMLInputElement
    expect(notificationsCheckbox.checked).toBe(false)

    const notificationEmailInput = screen.getByLabelText('Email auquel envoyer les notifications') as HTMLInputElement
    expect(notificationEmailInput.value).toBe('')
  })
})
