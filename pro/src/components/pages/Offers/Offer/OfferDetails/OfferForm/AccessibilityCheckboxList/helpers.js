export const getAccessibilityValues = values => {
  const accessibility = {
    audioDisabilityCompliant: values.audioDisabilityCompliant,
    mentalDisabilityCompliant: values.mentalDisabilityCompliant,
    motorDisabilityCompliant: values.motorDisabilityCompliant,
    visualDisabilityCompliant: values.visualDisabilityCompliant,
  }

  return Object.keys(accessibility).reduce((acc, fieldName) => {
    let fieldValue = accessibility[fieldName]
    if (fieldValue === undefined) {
      fieldValue = null
    }
    return { ...acc, [fieldName]: fieldValue }
  }, {})
}

export const checkHasNoDisabilityCompliance = values => {
  const disabilityCompliantValues = Object.values(getAccessibilityValues(values))
  const unknownDisabilityCompliance = disabilityCompliantValues.includes(null)
  const hasDisabilityCompliance = disabilityCompliantValues.includes(true)
  if (hasDisabilityCompliance || unknownDisabilityCompliance) {
    return false
  }

  return true
}

export const getAccessibilityInitialValues = ({ offer = null, venue = null }) => {
  const emptyAccessibility = {
    audioDisabilityCompliant: null,
    mentalDisabilityCompliant: null,
    motorDisabilityCompliant: null,
    visualDisabilityCompliant: null,
  }

  let accessibility = offer ? getAccessibilityValues(offer) : { ...emptyAccessibility }
  if (Object.values(accessibility).includes(null)) {
    accessibility = venue ? getAccessibilityValues(venue) : { ...emptyAccessibility }
  }
  accessibility.noDisabilityCompliant = checkHasNoDisabilityCompliance(accessibility)
  accessibility = Object.keys(accessibility).reduce(
    (acc, fieldName) => ({ ...acc, [fieldName]: !!accessibility[fieldName] }),
    {}
  )
  return accessibility
}
