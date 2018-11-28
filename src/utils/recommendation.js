export function setUniqIdOnRecommendation(recommendation) {
  const { mediation, offer } = recommendation
  const { eventId, thingId } = offer || {}
  const { tutoIndex } = mediation || {}
  let uniqId
  if (eventId) {
    uniqId = `event_${eventId}`
  } else if (thingId) {
    uniqId = `thing_${thingId}`
  } else if (typeof tutoIndex !== 'undefined') {
    uniqId = `tuto_${tutoIndex}`
  }
  return Object.assign({ uniqId }, recommendation)
}

const toto = ''

export default toto
