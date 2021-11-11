/*
* @debt directory "Gaël: this file should be migrated within the new directory structure"
*/

const createVenueForOffererUrl = offerers => {
  let url = ''

  if (offerers.length > 0) {
    const firstOffererIdOnList = offerers[0].id
    url = `/structures/${firstOffererIdOnList}/lieux/creation`
  }

  return url
}

export default createVenueForOffererUrl
