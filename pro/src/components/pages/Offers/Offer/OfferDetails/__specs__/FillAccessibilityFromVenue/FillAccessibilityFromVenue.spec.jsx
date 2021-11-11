import '@testing-library/jest-dom'
import { fireEvent, screen } from '@testing-library/react'

import {
  getOfferInputForField,
  setOfferValues,
} from '../helpers'

import {
  initialize,
} from './helpers'
import {
  offerAccessible,
  offerUndefinedAccessibility,
  offerUndefinedAccessibilityVenueAccessible,
  offerer2,
  offerer2VenuePhysicalAccessible,
  venueVirtual,
  venuePhysicalAccessible,
  venuePhysicalUndefinedAccessibility,
} from './mocks'


describe('should initialize creation form with venue accessibility from query params', () => {
  it("should have empty accessibilty when venue don't have accessibility set.", async () => {
    await initialize({
      selectedVenueFromUrl: venuePhysicalUndefinedAccessibility,
      selectedSubcategoryId: 'ID_SUB_CATEGORY_1_ONLINE_OR_OFFLINE'
    })

    expect(await getOfferInputForField('audioDisabilityCompliant')).not.toBeChecked()
    expect(await getOfferInputForField('mentalDisabilityCompliant')).not.toBeChecked()
    expect(await getOfferInputForField('motorDisabilityCompliant')).not.toBeChecked()
    expect(await getOfferInputForField('visualDisabilityCompliant')).not.toBeChecked()
    expect(await getOfferInputForField('noDisabilityCompliant')).not.toBeChecked()
  })

  it("should have venue accessibilty when venue have accessibility set.", async () => {
    await initialize({
      selectedVenueFromUrl: venuePhysicalAccessible,
      selectedSubcategoryId: 'ID_SUB_CATEGORY_1_ONLINE_OR_OFFLINE'
    })

    expect(await getOfferInputForField('audioDisabilityCompliant')).toBeChecked()
    expect(await getOfferInputForField('mentalDisabilityCompliant')).not.toBeChecked()
    expect(await getOfferInputForField('motorDisabilityCompliant')).toBeChecked()
    expect(await getOfferInputForField('visualDisabilityCompliant')).not.toBeChecked()
    expect(await getOfferInputForField('noDisabilityCompliant')).not.toBeChecked()
  })
})

describe('should initialize edition form', () => {
  it("should have offer accessibilty if it's set.", async () => {
    await initialize({
      offer: offerAccessible,
    })

    expect(await getOfferInputForField('audioDisabilityCompliant')).not.toBeChecked()
    expect(await getOfferInputForField('mentalDisabilityCompliant')).toBeChecked()
    expect(await getOfferInputForField('motorDisabilityCompliant')).not.toBeChecked()
    expect(await getOfferInputForField('visualDisabilityCompliant')).toBeChecked()
    expect(await getOfferInputForField('noDisabilityCompliant')).not.toBeChecked()
  })

  it("should have venue accessibilty venue have accessibility and offer don't.", async () => {
    await initialize({
      offer: offerUndefinedAccessibilityVenueAccessible,
    })

    expect(await getOfferInputForField('audioDisabilityCompliant')).toBeChecked()
    expect(await getOfferInputForField('mentalDisabilityCompliant')).not.toBeChecked()
    expect(await getOfferInputForField('motorDisabilityCompliant')).toBeChecked()
    expect(await getOfferInputForField('visualDisabilityCompliant')).not.toBeChecked()
    expect(await getOfferInputForField('noDisabilityCompliant')).not.toBeChecked()
  })

  it("should be empty if neither offer and venue have accessibility.", async () => {
    await initialize({
      offer: offerUndefinedAccessibility,
    })

    expect(await getOfferInputForField('audioDisabilityCompliant')).not.toBeChecked()
    expect(await getOfferInputForField('mentalDisabilityCompliant')).not.toBeChecked()
    expect(await getOfferInputForField('motorDisabilityCompliant')).not.toBeChecked()
    expect(await getOfferInputForField('visualDisabilityCompliant')).not.toBeChecked()
    expect(await getOfferInputForField('noDisabilityCompliant')).not.toBeChecked()
  })
})

describe('test creation form venue edition', () => {
  it("should set venue accessibility when venue change.", async () => {
    await initialize({
      selectedVenueFromUrl: venuePhysicalUndefinedAccessibility,
      selectedSubcategoryId: 'ID_SUB_CATEGORY_1_ONLINE_OR_OFFLINE'
    })

    setOfferValues({ venueId: venuePhysicalAccessible.id })
    expect(await getOfferInputForField('audioDisabilityCompliant')).toBeChecked()
    expect(await getOfferInputForField('mentalDisabilityCompliant')).not.toBeChecked()
    expect(await getOfferInputForField('motorDisabilityCompliant')).toBeChecked()
    expect(await getOfferInputForField('visualDisabilityCompliant')).not.toBeChecked()
    expect(await getOfferInputForField('noDisabilityCompliant')).not.toBeChecked()

    // virtual venues have all accessibility values as null
    setOfferValues({ venueId: venueVirtual.id })
    expect(await getOfferInputForField('audioDisabilityCompliant')).not.toBeChecked()
    expect(await getOfferInputForField('mentalDisabilityCompliant')).not.toBeChecked()
    expect(await getOfferInputForField('motorDisabilityCompliant')).not.toBeChecked()
    expect(await getOfferInputForField('visualDisabilityCompliant')).not.toBeChecked()
    expect(await getOfferInputForField('noDisabilityCompliant')).not.toBeChecked()
  })

  it("should set venue accessibility when subCategory change.", async () => {
    await initialize({
      selectedVenueFromUrl: venuePhysicalAccessible,
      selectedSubcategoryId: 'ID_SUB_CATEGORY_1_ONLINE_OR_OFFLINE'
    })
    setOfferValues({ subcategoryId: 'ID_SUB_CATEGORY_1_ONLINE' })

    expect(await getOfferInputForField('audioDisabilityCompliant')).not.toBeChecked()
    expect(await getOfferInputForField('mentalDisabilityCompliant')).not.toBeChecked()
    expect(await getOfferInputForField('motorDisabilityCompliant')).not.toBeChecked()
    expect(await getOfferInputForField('visualDisabilityCompliant')).not.toBeChecked()
    expect(await getOfferInputForField('noDisabilityCompliant')).not.toBeChecked()
  })
})

describe('test creation form offerer edition', () => {
  it("should set venue accessibility when offerer change.", async () => {
    await initialize({
      selectedVenue: venuePhysicalAccessible,
      selectedSubcategoryId: 'ID_SUB_CATEGORY_1_OFFLINE',
    })

    setOfferValues({
      offererId: offerer2.id,
      venueId: offerer2VenuePhysicalAccessible.id
    })
    await screen.findByDisplayValue(offerer2VenuePhysicalAccessible.name)
    expect(await getOfferInputForField('audioDisabilityCompliant')).toBeChecked()
    expect(await getOfferInputForField('mentalDisabilityCompliant')).toBeChecked()
    expect(await getOfferInputForField('motorDisabilityCompliant')).toBeChecked()
    expect(await getOfferInputForField('visualDisabilityCompliant')).toBeChecked()
    expect(await getOfferInputForField('noDisabilityCompliant')).not.toBeChecked()
  })
})

describe('test accessibily checkbox click', () => {
  it('should compute checkbox values', async () => {
    // Given
    await initialize({
      offer: offerUndefinedAccessibility,
    })

    const accessibilityCheckboxes = {
      audioDisabilityCompliant: await getOfferInputForField('audioDisabilityCompliant'),
      mentalDisabilityCompliant: await getOfferInputForField('mentalDisabilityCompliant'),
      motorDisabilityCompliant: await getOfferInputForField('motorDisabilityCompliant'),
      visualDisabilityCompliant: await getOfferInputForField('visualDisabilityCompliant'),
      noDisabilityCompliant: await getOfferInputForField('noDisabilityCompliant'),
    }

    // initial value are empty, all values are false
    expect(accessibilityCheckboxes.audioDisabilityCompliant).not.toBeChecked()
    expect(accessibilityCheckboxes.mentalDisabilityCompliant).not.toBeChecked()
    expect(accessibilityCheckboxes.motorDisabilityCompliant).not.toBeChecked()
    expect(accessibilityCheckboxes.visualDisabilityCompliant).not.toBeChecked()
    expect(accessibilityCheckboxes.noDisabilityCompliant).not.toBeChecked()

    // one accessibility true, other falses
    await fireEvent.click(accessibilityCheckboxes.audioDisabilityCompliant)
    expect(accessibilityCheckboxes.audioDisabilityCompliant).toBeChecked()
    expect(accessibilityCheckboxes.mentalDisabilityCompliant).not.toBeChecked()
    expect(accessibilityCheckboxes.motorDisabilityCompliant).not.toBeChecked()
    expect(accessibilityCheckboxes.visualDisabilityCompliant).not.toBeChecked()
    expect(accessibilityCheckboxes.noDisabilityCompliant).not.toBeChecked()

    // all accessibility false, noDisabilityCompliant should be true
    await fireEvent.click(accessibilityCheckboxes.audioDisabilityCompliant)
    expect(accessibilityCheckboxes.audioDisabilityCompliant).not.toBeChecked()
    expect(accessibilityCheckboxes.mentalDisabilityCompliant).not.toBeChecked()
    expect(accessibilityCheckboxes.motorDisabilityCompliant).not.toBeChecked()
    expect(accessibilityCheckboxes.visualDisabilityCompliant).not.toBeChecked()
    expect(accessibilityCheckboxes.noDisabilityCompliant).toBeChecked()

    // again, one accessibility true, other falses
    await fireEvent.click(accessibilityCheckboxes.audioDisabilityCompliant)
    expect(accessibilityCheckboxes.audioDisabilityCompliant).toBeChecked()
    expect(accessibilityCheckboxes.mentalDisabilityCompliant).not.toBeChecked()
    expect(accessibilityCheckboxes.motorDisabilityCompliant).not.toBeChecked()
    expect(accessibilityCheckboxes.visualDisabilityCompliant).not.toBeChecked()
    expect(accessibilityCheckboxes.noDisabilityCompliant).not.toBeChecked()

    // click on noDisabilityCompliant should change other accessibility to false
    await fireEvent.click(accessibilityCheckboxes.noDisabilityCompliant)
    expect(accessibilityCheckboxes.audioDisabilityCompliant).not.toBeChecked()
    expect(accessibilityCheckboxes.mentalDisabilityCompliant).not.toBeChecked()
    expect(accessibilityCheckboxes.motorDisabilityCompliant).not.toBeChecked()
    expect(accessibilityCheckboxes.visualDisabilityCompliant).not.toBeChecked()
    expect(accessibilityCheckboxes.noDisabilityCompliant).toBeChecked()

    // a second click on noDisabilityCompliant shouldn't change values
    await fireEvent.click(accessibilityCheckboxes.noDisabilityCompliant)
    expect(accessibilityCheckboxes.audioDisabilityCompliant).not.toBeChecked()
    expect(accessibilityCheckboxes.mentalDisabilityCompliant).not.toBeChecked()
    expect(accessibilityCheckboxes.motorDisabilityCompliant).not.toBeChecked()
    expect(accessibilityCheckboxes.visualDisabilityCompliant).not.toBeChecked()
    expect(accessibilityCheckboxes.noDisabilityCompliant).toBeChecked()
  })
})
