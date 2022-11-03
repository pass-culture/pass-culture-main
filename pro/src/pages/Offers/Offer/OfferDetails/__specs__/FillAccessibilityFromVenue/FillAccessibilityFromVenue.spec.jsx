import '@testing-library/jest-dom'

import { screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'

import { setOfferValues } from '../helpers'

import { initialize } from './helpers'
import {
  offerAccessible,
  offerUndefinedAccessibility,
  offerUndefinedAccessibilityVenueAccessible,
  offerer2,
  offerer2VenuePhysicalAccessible,
  venuePhysicalAccessible,
  venuePhysicalUndefinedAccessibility,
  venueVirtual,
} from './mocks'

describe('should initialize creation form with venue accessibility from query params', () => {
  it("should have empty accessibilty when venue don't have accessibility set.", async () => {
    await initialize({
      selectedVenueFromUrl: venuePhysicalUndefinedAccessibility,
      selectedSubcategoryId: 'ID_SUB_CATEGORY_1_ONLINE_OR_OFFLINE',
    })
    screen.getByLabelText(/Auditif/)
    expect(screen.getByLabelText(/Auditif/)).not.toBeChecked()
    expect(screen.getByLabelText(/Psychique ou cognitif/)).not.toBeChecked()
    expect(screen.getByLabelText(/Moteur/)).not.toBeChecked()
    expect(screen.getByLabelText(/Visuel/)).not.toBeChecked()
    expect(screen.getByLabelText(/Non accessible/)).not.toBeChecked()
  })

  it('should have venue accessibilty when venue have accessibility set.', async () => {
    await initialize({
      selectedVenueFromUrl: venuePhysicalAccessible,
      selectedSubcategoryId: 'ID_SUB_CATEGORY_1_ONLINE_OR_OFFLINE',
    })

    expect(screen.getByLabelText(/Auditif/)).toBeChecked()
    expect(screen.getByLabelText(/Psychique ou cognitif/)).not.toBeChecked()
    expect(screen.getByLabelText(/Moteur/)).toBeChecked()
    expect(screen.getByLabelText(/Visuel/)).not.toBeChecked()
    expect(screen.getByLabelText(/Non accessible/)).not.toBeChecked()
  })
})

describe('should initialize edition form', () => {
  it("should have offer accessibilty if it's set.", async () => {
    await initialize({
      offer: offerAccessible,
    })

    expect(screen.getByLabelText(/Auditif/)).not.toBeChecked()
    expect(screen.getByLabelText(/Psychique ou cognitif/)).toBeChecked()
    expect(screen.getByLabelText(/Moteur/)).not.toBeChecked()
    expect(screen.getByLabelText(/Visuel/)).toBeChecked()
    expect(screen.getByLabelText(/Non accessible/)).not.toBeChecked()
  })

  it("should have venue accessibilty venue have accessibility and offer don't.", async () => {
    await initialize({
      offer: offerUndefinedAccessibilityVenueAccessible,
    })

    expect(screen.getByLabelText(/Auditif/)).toBeChecked()
    expect(screen.getByLabelText(/Psychique ou cognitif/)).not.toBeChecked()
    expect(screen.getByLabelText(/Moteur/)).toBeChecked()
    expect(screen.getByLabelText(/Visuel/)).not.toBeChecked()
    expect(screen.getByLabelText(/Non accessible/)).not.toBeChecked()
  })

  it('should be empty if neither offer and venue have accessibility.', async () => {
    await initialize({
      offer: offerUndefinedAccessibility,
    })

    expect(screen.getByLabelText(/Auditif/)).not.toBeChecked()
    expect(screen.getByLabelText(/Psychique ou cognitif/)).not.toBeChecked()
    expect(screen.getByLabelText(/Moteur/)).not.toBeChecked()
    expect(screen.getByLabelText(/Visuel/)).not.toBeChecked()
    expect(screen.getByLabelText(/Non accessible/)).not.toBeChecked()
  })
})

describe('test creation form venue edition', () => {
  it('should set venue accessibility when venue change.', async () => {
    await initialize({
      selectedVenueFromUrl: venuePhysicalUndefinedAccessibility,
      selectedSubcategoryId: 'ID_SUB_CATEGORY_1_ONLINE_OR_OFFLINE',
    })
    await setOfferValues({ venueId: venuePhysicalAccessible.id })

    expect(screen.getByLabelText(/Auditif/)).toBeChecked()
    expect(screen.getByLabelText(/Psychique ou cognitif/)).not.toBeChecked()
    expect(screen.getByLabelText(/Moteur/)).toBeChecked()
    expect(screen.getByLabelText(/Visuel/)).not.toBeChecked()
    expect(screen.getByLabelText(/Non accessible/)).not.toBeChecked()

    // virtual venues have all accessibility values as null
    await setOfferValues({ venueId: venueVirtual.id })
    expect(screen.getByLabelText(/Auditif/)).not.toBeChecked()
    expect(screen.getByLabelText(/Psychique ou cognitif/)).not.toBeChecked()
    expect(screen.getByLabelText(/Moteur/)).not.toBeChecked()
    expect(screen.getByLabelText(/Visuel/)).not.toBeChecked()
    expect(screen.getByLabelText(/Non accessible/)).not.toBeChecked()
  })

  it('should set venue accessibility when subCategory change.', async () => {
    await initialize({
      selectedVenueFromUrl: venuePhysicalAccessible,
      selectedSubcategoryId: 'ID_SUB_CATEGORY_1_ONLINE_OR_OFFLINE',
    })

    await setOfferValues({ subcategoryId: 'ID_SUB_CATEGORY_1_ONLINE' })

    expect(screen.getByLabelText(/Auditif/)).not.toBeChecked()
    expect(screen.getByLabelText(/Psychique ou cognitif/)).not.toBeChecked()
    expect(screen.getByLabelText(/Moteur/)).not.toBeChecked()
    expect(screen.getByLabelText(/Visuel/)).not.toBeChecked()
    expect(screen.getByLabelText(/Non accessible/)).not.toBeChecked()
  })
})

describe('test creation form offerer edition', () => {
  it('should set venue accessibility when offerer change.', async () => {
    await initialize({
      selectedVenue: venuePhysicalAccessible,
      selectedSubcategoryId: 'ID_SUB_CATEGORY_1_OFFLINE',
    })

    await setOfferValues({
      offererId: offerer2.id,
      venueId: offerer2VenuePhysicalAccessible.id,
    })

    await screen.findByDisplayValue(offerer2VenuePhysicalAccessible.name)
    expect(screen.getByLabelText(/Auditif/)).toBeChecked()
    expect(screen.getByLabelText(/Psychique ou cognitif/)).toBeChecked()
    expect(screen.getByLabelText(/Moteur/)).toBeChecked()
    expect(screen.getByLabelText(/Visuel/)).toBeChecked()
    expect(screen.getByLabelText(/Non accessible/)).not.toBeChecked()
  })
})

describe('test accessibily checkbox click', () => {
  it('should compute checkbox values', async () => {
    // Given
    await initialize({
      offer: offerUndefinedAccessibility,
    })

    const accessibilityCheckboxes = {
      audioDisabilityCompliant: screen.getByLabelText(/Auditif/),
      mentalDisabilityCompliant: screen.getByLabelText(/Psychique ou cognitif/),
      motorDisabilityCompliant: screen.getByLabelText(/Moteur/),
      visualDisabilityCompliant: screen.getByLabelText(/Visuel/),
      noDisabilityCompliant: screen.getByLabelText(/Non accessible/),
    }

    // initial value are empty, all values are false
    expect(accessibilityCheckboxes.audioDisabilityCompliant).not.toBeChecked()
    expect(accessibilityCheckboxes.mentalDisabilityCompliant).not.toBeChecked()
    expect(accessibilityCheckboxes.motorDisabilityCompliant).not.toBeChecked()
    expect(accessibilityCheckboxes.visualDisabilityCompliant).not.toBeChecked()
    expect(accessibilityCheckboxes.noDisabilityCompliant).not.toBeChecked()

    // one accessibility true, other falses
    await userEvent.click(accessibilityCheckboxes.audioDisabilityCompliant)
    expect(accessibilityCheckboxes.audioDisabilityCompliant).toBeChecked()
    expect(accessibilityCheckboxes.mentalDisabilityCompliant).not.toBeChecked()
    expect(accessibilityCheckboxes.motorDisabilityCompliant).not.toBeChecked()
    expect(accessibilityCheckboxes.visualDisabilityCompliant).not.toBeChecked()
    expect(accessibilityCheckboxes.noDisabilityCompliant).not.toBeChecked()

    // all accessibility false, noDisabilityCompliant should be true
    await userEvent.click(accessibilityCheckboxes.audioDisabilityCompliant)
    expect(accessibilityCheckboxes.audioDisabilityCompliant).not.toBeChecked()
    expect(accessibilityCheckboxes.mentalDisabilityCompliant).not.toBeChecked()
    expect(accessibilityCheckboxes.motorDisabilityCompliant).not.toBeChecked()
    expect(accessibilityCheckboxes.visualDisabilityCompliant).not.toBeChecked()
    expect(accessibilityCheckboxes.noDisabilityCompliant).toBeChecked()

    // again, one accessibility true, other falses
    await userEvent.click(accessibilityCheckboxes.audioDisabilityCompliant)
    expect(accessibilityCheckboxes.audioDisabilityCompliant).toBeChecked()
    expect(accessibilityCheckboxes.mentalDisabilityCompliant).not.toBeChecked()
    expect(accessibilityCheckboxes.motorDisabilityCompliant).not.toBeChecked()
    expect(accessibilityCheckboxes.visualDisabilityCompliant).not.toBeChecked()
    expect(accessibilityCheckboxes.noDisabilityCompliant).not.toBeChecked()

    // click on noDisabilityCompliant should change other accessibility to false
    await userEvent.click(accessibilityCheckboxes.noDisabilityCompliant)
    expect(accessibilityCheckboxes.audioDisabilityCompliant).not.toBeChecked()
    expect(accessibilityCheckboxes.mentalDisabilityCompliant).not.toBeChecked()
    expect(accessibilityCheckboxes.motorDisabilityCompliant).not.toBeChecked()
    expect(accessibilityCheckboxes.visualDisabilityCompliant).not.toBeChecked()
    expect(accessibilityCheckboxes.noDisabilityCompliant).toBeChecked()

    // a second click on noDisabilityCompliant shouldn't change values
    await userEvent.click(accessibilityCheckboxes.noDisabilityCompliant)
    expect(accessibilityCheckboxes.audioDisabilityCompliant).not.toBeChecked()
    expect(accessibilityCheckboxes.mentalDisabilityCompliant).not.toBeChecked()
    expect(accessibilityCheckboxes.motorDisabilityCompliant).not.toBeChecked()
    expect(accessibilityCheckboxes.visualDisabilityCompliant).not.toBeChecked()
    expect(accessibilityCheckboxes.noDisabilityCompliant).toBeChecked()
  })
})
