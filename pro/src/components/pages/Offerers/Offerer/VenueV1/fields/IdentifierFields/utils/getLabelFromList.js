/*
* @debt complexity "Gaël: file nested too deep in directory structure"
*/

const getLabelFromList = (venueTypes, venueTypeId) => {
  const venueType = venueTypes.find(venueType => {
    return venueType.id === venueTypeId
  })
  return venueType ? venueType.label : '-'
}

export default getLabelFromList
