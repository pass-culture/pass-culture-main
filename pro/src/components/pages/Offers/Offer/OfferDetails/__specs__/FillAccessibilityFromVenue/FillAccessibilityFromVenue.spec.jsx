import '@testing-library/jest-dom'

import { fireEvent, screen } from '@testing-library/react'

import { getOfferInputForField, setOfferValues } from '../helpers'

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

    await expect(
      getOfferInputForField('audioDisabilityCompliant')
    ).resolves.not.toBeChecked()
    await expect(
      getOfferInputForField('mentalDisabilityCompliant')
    ).resolves.not.toBeChecked()
    await expect(
      getOfferInputForField('motorDisabilityCompliant')
    ).resolves.not.toBeChecked()
    await expect(
      getOfferInputForField('visualDisabilityCompliant')
    ).resolves.not.toBeChecked()
    await expect(
      getOfferInputForField('noDisabilityCompliant')
    ).resolves.not.toBeChecked()
  })

  it('should have venue accessibilty when venue have accessibility set.', async () => {
    await initialize({
      selectedVenueFromUrl: venuePhysicalAccessible,
      selectedSubcategoryId: 'ID_SUB_CATEGORY_1_ONLINE_OR_OFFLINE',
    })

    await expect(
      getOfferInputForField('audioDisabilityCompliant')
    ).resolves.toBeChecked()
    await expect(
      getOfferInputForField('mentalDisabilityCompliant')
    ).resolves.not.toBeChecked()
    await expect(
      getOfferInputForField('motorDisabilityCompliant')
    ).resolves.toBeChecked()
    await expect(
      getOfferInputForField('visualDisabilityCompliant')
    ).resolves.not.toBeChecked()
    await expect(
      getOfferInputForField('noDisabilityCompliant')
    ).resolves.not.toBeChecked()
  })
})

describe('should initialize edition form', () => {
  it("should have offer accessibilty if it's set.", async () => {
    await initialize({
      offer: offerAccessible,
    })

    await expect(
      getOfferInputForField('audioDisabilityCompliant')
    ).resolves.not.toBeChecked()
    await expect(
      getOfferInputForField('mentalDisabilityCompliant')
    ).resolves.toBeChecked()
    await expect(
      getOfferInputForField('motorDisabilityCompliant')
    ).resolves.not.toBeChecked()
    await expect(
      getOfferInputForField('visualDisabilityCompliant')
    ).resolves.toBeChecked()
    await expect(
      getOfferInputForField('noDisabilityCompliant')
    ).resolves.not.toBeChecked()
  })

  it("should have venue accessibilty venue have accessibility and offer don't.", async () => {
    await initialize({
      offer: offerUndefinedAccessibilityVenueAccessible,
    })

    await expect(
      getOfferInputForField('audioDisabilityCompliant')
    ).resolves.toBeChecked()
    await expect(
      getOfferInputForField('mentalDisabilityCompliant')
    ).resolves.not.toBeChecked()
    await expect(
      getOfferInputForField('motorDisabilityCompliant')
    ).resolves.toBeChecked()
    await expect(
      getOfferInputForField('visualDisabilityCompliant')
    ).resolves.not.toBeChecked()
    await expect(
      getOfferInputForField('noDisabilityCompliant')
    ).resolves.not.toBeChecked()
  })

  it('should be empty if neither offer and venue have accessibility.', async () => {
    await initialize({
      offer: offerUndefinedAccessibility,
    })

    await expect(
      getOfferInputForField('audioDisabilityCompliant')
    ).resolves.not.toBeChecked()
    await expect(
      getOfferInputForField('mentalDisabilityCompliant')
    ).resolves.not.toBeChecked()
    await expect(
      getOfferInputForField('motorDisabilityCompliant')
    ).resolves.not.toBeChecked()
    await expect(
      getOfferInputForField('visualDisabilityCompliant')
    ).resolves.not.toBeChecked()
    await expect(
      getOfferInputForField('noDisabilityCompliant')
    ).resolves.not.toBeChecked()
  })
})

describe('test creation form venue edition', () => {
  it('should set venue accessibility when venue change.', async () => {
    await initialize({
      selectedVenueFromUrl: venuePhysicalUndefinedAccessibility,
      selectedSubcategoryId: 'ID_SUB_CATEGORY_1_ONLINE_OR_OFFLINE',
    })
    await setOfferValues({ venueId: venuePhysicalAccessible.id })

    await expect(
      getOfferInputForField('audioDisabilityCompliant')
    ).resolves.toBeChecked()
    await expect(
      getOfferInputForField('mentalDisabilityCompliant')
    ).resolves.not.toBeChecked()
    await expect(
      getOfferInputForField('motorDisabilityCompliant')
    ).resolves.toBeChecked()
    await expect(
      getOfferInputForField('visualDisabilityCompliant')
    ).resolves.not.toBeChecked()
    await expect(
      getOfferInputForField('noDisabilityCompliant')
    ).resolves.not.toBeChecked()

    // virtual venues have all accessibility values as null
    await setOfferValues({ venueId: venueVirtual.id })
    await expect(
      getOfferInputForField('audioDisabilityCompliant')
    ).resolves.not.toBeChecked()
    await expect(
      getOfferInputForField('mentalDisabilityCompliant')
    ).resolves.not.toBeChecked()
    await expect(
      getOfferInputForField('motorDisabilityCompliant')
    ).resolves.not.toBeChecked()
    await expect(
      getOfferInputForField('visualDisabilityCompliant')
    ).resolves.not.toBeChecked()
    await expect(
      getOfferInputForField('noDisabilityCompliant')
    ).resolves.not.toBeChecked()
  })

  it('should set venue accessibility when subCategory change.', async () => {
    await initialize({
      selectedVenueFromUrl: venuePhysicalAccessible,
      selectedSubcategoryId: 'ID_SUB_CATEGORY_1_ONLINE_OR_OFFLINE',
    })

    await setOfferValues({ subcategoryId: 'ID_SUB_CATEGORY_1_ONLINE' })

    await expect(
      getOfferInputForField('audioDisabilityCompliant')
    ).resolves.not.toBeChecked()
    await expect(
      getOfferInputForField('mentalDisabilityCompliant')
    ).resolves.not.toBeChecked()
    await expect(
      getOfferInputForField('motorDisabilityCompliant')
    ).resolves.not.toBeChecked()
    await expect(
      getOfferInputForField('visualDisabilityCompliant')
    ).resolves.not.toBeChecked()
    await expect(
      getOfferInputForField('noDisabilityCompliant')
    ).resolves.not.toBeChecked()
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
    await expect(
      getOfferInputForField('audioDisabilityCompliant')
    ).resolves.toBeChecked()
    await expect(
      getOfferInputForField('mentalDisabilityCompliant')
    ).resolves.toBeChecked()
    await expect(
      getOfferInputForField('motorDisabilityCompliant')
    ).resolves.toBeChecked()
    await expect(
      getOfferInputForField('visualDisabilityCompliant')
    ).resolves.toBeChecked()
    await expect(
      getOfferInputForField('noDisabilityCompliant')
    ).resolves.not.toBeChecked()
  })
})

describe('test accessibily checkbox click', () => {
  it('should compute checkbox values', async () => {
    // Given
    await initialize({
      offer: offerUndefinedAccessibility,
    })

    const accessibilityCheckboxes = {
      audioDisabilityCompliant: await getOfferInputForField(
        'audioDisabilityCompliant'
      ),
      mentalDisabilityCompliant: await getOfferInputForField(
        'mentalDisabilityCompliant'
      ),
      motorDisabilityCompliant: await getOfferInputForField(
        'motorDisabilityCompliant'
      ),
      visualDisabilityCompliant: await getOfferInputForField(
        'visualDisabilityCompliant'
      ),
      noDisabilityCompliant: await getOfferInputForField(
        'noDisabilityCompliant'
      ),
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
