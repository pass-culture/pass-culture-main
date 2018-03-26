// import { rgb_to_hsv } from 'colorsys'
import { API_URL, THUMBS_URL } from '../utils/config'

export function getContentFromUserMediation (userMediation) {
  // check and unpack
  if (!userMediation) {
    return
  }
  const { mediation,
    userMediationOffers
  } = userMediation
  // choose one of the associated offer
  // for now we just pick randomly one of them
  // and this is actually what we want for the case where we have an event
  // proposed by several ticketers
  const chosenOffer = userMediationOffers &&
    userMediationOffers[Math.floor(Math.random() * userMediationOffers.length)]
  // check
  if (!chosenOffer && !mediation) {
    return
  }
  // source
  let source
  let sourceCollectionName
  let venue
  if (!mediation && chosenOffer) {
    if (chosenOffer.eventOccurence) {
      source = chosenOffer.eventOccurence
      sourceCollectionName = 'eventOccurences'
    } else {
      source = chosenOffer.thing
      sourceCollectionName = 'things'
    }
  } else {
    if (mediation.event) {
      source = mediation.event
      sourceCollectionName = 'events'
      venue = chosenOffer.eventOccurence.venue
    } else {
      source = mediation.thing
      sourceCollectionName = 'things'
    }
  }
  // venue
  venue = venue || chosenOffer.venue || (source && source.venue)
  // color
  let backgroundColor
  let thumbUrl
  // TODO: colorsys.rgb_to_hsv({ r: 255, g: 255, b: 255 }) ...
  if (mediation && mediation.thumbCount > 0) {
    thumbUrl = `${THUMBS_URL}/mediations/${mediation.id}`
    backgroundColor = mediation.firstThumbDominantColor
  } else if (source && source.thumbCount > 0) {
    thumbUrl = `${THUMBS_URL}/${sourceCollectionName}/${source.id}`
    backgroundColor = source.firstThumbDominantColor
  } else {
    thumbUrl = `${API_URL}/static/images/default_thumb.png`
    backgroundColor = [0, 0, 0]
  }
  return Object.assign({ backgroundColor,
    chosenOffer,
    source,
    thumbUrl,
    venue
  }, userMediation)
}
