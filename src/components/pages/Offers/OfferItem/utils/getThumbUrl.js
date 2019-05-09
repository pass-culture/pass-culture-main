const getThumbUrl = mediations => {
  const emptyUrl = ''
  const hasMediations = mediations && mediations.length > 0

  return hasMediations ? mediations[0].thumbUrl : emptyUrl
}

export default getThumbUrl
