export const REGEX_STARTING_WITH_NUMBERS = /^\d/

export const buildPlaceLabel = (place) => {
  if (!place) {
    return 'Choisir un lieu'
  }

  if (REGEX_STARTING_WITH_NUMBERS.test(place.name.long)) {
    return place.name.long
  }

  return place.name.short
}
