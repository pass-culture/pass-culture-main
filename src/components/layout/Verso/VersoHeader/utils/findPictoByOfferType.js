import { ICONS_URL } from '../../../../../utils/config'

const CATEGORIES_ICONS = {
  AUDIOVISUEL: 'musique',
  CINEMA: 'cinema',
  CINEMA_ABO: 'cinema',
  CONFERENCE_DEBAT_DEDICACE: 'conference',
  INSTRUMENT: 'atelier',
  JEUX: 'jeu',
  JEUX_VIDEO_ABO: 'jeu',
  JEUX_VIDEO: 'jeu',
  LIVRE_AUDIO: 'livre',
  LIVRE_EDITION: 'livre',
  MUSEES_PATRIMOINE: 'visite',
  MUSEES_PATRIMOINE_ABO: 'visite',
  MUSIQUE_ABO: 'musique',
  MUSIQUE: 'musique',
  OEUVRE_ART: 'visite',
  PRATIQUE_ARTISTIQUE_ABO: 'atelier',
  PRATIQUE_ARTISTIQUE: 'atelier',
  PRESSE_ABO: 'livre',
  SPECTACLE_VIVANT: 'spectacle',
  SPECTACLE_VIVANT_ABO: 'spectacle',
}

const findPictoByOfferType = (offerType) => {
  if (!offerType) {
    return null
  }

  const category = offerType.split('.')
  const picto = CATEGORIES_ICONS[category[1]]

  return `${ICONS_URL}/picto-${picto}.svg`
}

export default findPictoByOfferType
