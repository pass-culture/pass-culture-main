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
  const disabilityCompliantValues = Object.values(
    getAccessibilityValues(values)
  )
  const unknownDisabilityCompliance = disabilityCompliantValues.includes(null)
  const hasDisabilityCompliance = disabilityCompliantValues.includes(true)
  if (hasDisabilityCompliance || unknownDisabilityCompliance) {
    return false
  }

  return true
}