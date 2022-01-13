/*
 * @debt complexity "Gaël: file nested too deep in directory structure"
 */

const getLabelFromList = (venueTypes, venueTypeCode) => {
  const venueType = venueTypes.find(venueType => {
    return venueType.id === venueTypeCode
  })
  return venueType ? venueType.label : '-'
}

export default getLabelFromList
