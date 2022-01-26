import '@testing-library/jest-dom'
import { screen, render } from '@testing-library/react'
import { createBrowserHistory } from 'history'
import React from 'react'
import { Router } from 'react-router'

import {
  getCategoriesSelect,
  getSubcategoriesSelect,
  selectOffererAndVenue,
} from '../__tests-utils__/eacOfferCreationUtils'
import setDefaultProps from '../__tests-utils__/setDefaultProps'
import {
  DESCRIPTION_LABEL,
  DURATION_LABEL,
  EMAIL_LABEL,
  NOTIFICATIONS_EMAIL_LABEL,
  NOTIFICATIONS_LABEL,
  EVENT_ADDRESS_OFFERER_LABEL,
  EVENT_ADDRESS_OTHER_LABEL,
  EVENT_ADDRESS_SCHOOL_LABEL,
  PHONE_LABEL,
  TITLE_LABEL,
} from '../constants/labels'
import OfferEducational, { IOfferEducationalProps } from '../OfferEducational'
import { accessibilityOptions } from '../OfferEducationalForm/FormAccessibility/accessibilityOptions'
import { participantsOptions } from '../OfferEducationalForm/FormParticipants/participantsOptions'

const renderEACOfferCreation = (
  props: IOfferEducationalProps,
  overrideProps?: Partial<IOfferEducationalProps>
) => {
  const history = createBrowserHistory()
  return render(
    <Router history={history}>
      <OfferEducational {...props} {...overrideProps} />
    </Router>
  )
}

const contains = (str: string): RegExp => new RegExp(`^.*${str}.*$`)

describe('screens | OfferEducational', () => {
  let props: IOfferEducationalProps

  beforeEach(() => {
    props = setDefaultProps()
  })

  it('should have no initial values', async () => {
    renderEACOfferCreation(props)

    await selectOffererAndVenue()

    const categoriesSelect = getCategoriesSelect()
    expect(categoriesSelect).toBeInTheDocument()
    expect(categoriesSelect).toHaveValue('')

    const subCategoriesSelect = getSubcategoriesSelect()
    expect(subCategoriesSelect).not.toBeInTheDocument()

    const titleInput = screen.getByLabelText(
      contains(TITLE_LABEL)
    ) as HTMLInputElement
    expect(titleInput).toHaveValue('')

    const descriptionTextArea = screen.getByLabelText(
      contains(DESCRIPTION_LABEL)
    ) as HTMLTextAreaElement
    expect(descriptionTextArea).toHaveValue('')

    const durationInput = screen.getByLabelText(DURATION_LABEL, {
      exact: false,
    }) as HTMLTextAreaElement
    expect(durationInput).toHaveValue('')

    const offerVenueRadio1 = screen.getByLabelText(
      EVENT_ADDRESS_OFFERER_LABEL
    ) as HTMLInputElement

    const offerVenueRadio2 = screen.getByLabelText(
      EVENT_ADDRESS_SCHOOL_LABEL
    ) as HTMLInputElement

    const offerVenueRadio3 = screen.getByLabelText(
      EVENT_ADDRESS_OTHER_LABEL
    ) as HTMLInputElement

    ;[offerVenueRadio2, offerVenueRadio3].forEach(radio => {
      expect(radio).not.toBeChecked()
    })

    expect(offerVenueRadio1).toBeChecked()

    participantsOptions.forEach(participantsOption => {
      const participantsCheckbox = screen.getByLabelText(
        participantsOption.label
      ) as HTMLInputElement
      expect(participantsCheckbox.checked).toBe(false)
    })

    accessibilityOptions.forEach(accessibilityOption => {
      const accessibilityCheckbox = screen.getByLabelText(
        accessibilityOption.label
      ) as HTMLInputElement
      expect(accessibilityCheckbox.checked).toBe(false)
    })

    const phoneInput = screen.getByLabelText(PHONE_LABEL) as HTMLInputElement
    expect(phoneInput).toHaveValue('')

    const emailInput = screen.getByLabelText(EMAIL_LABEL) as HTMLInputElement
    expect(emailInput).toHaveValue('')

    const notificationsCheckbox = screen.getByLabelText(
      NOTIFICATIONS_LABEL
    ) as HTMLInputElement
    expect(notificationsCheckbox.checked).toBe(false)

    const notificationEmailInput = screen.queryByLabelText(
      NOTIFICATIONS_EMAIL_LABEL
    ) as HTMLInputElement
    expect(notificationEmailInput).not.toBeInTheDocument()
  })
})
