import { BlockerFunction } from 'components/RouteLeavingGuard/RouteLeavingGuard'

const STEP_OFFER = 'offer'
const STEP_OFFER_EDITION = 'offer_edition'
const STEP_STOCKS = 'stocks'
const STEP_VISIBILITY = 'visibility'
const STEP_CONFIRMATION = 'confirmation'
const STEP_RECAP = 'summary'
const STEP_PREVIEW = 'preview'

const collectiveUrlPatterns: { [key: string]: RegExp } = {
  [STEP_OFFER]: /\/offre\/creation\/collectif/g,
  [STEP_OFFER_EDITION]: /\/offre\/collectif(\/vitrine)?\/[A-Z,0-9]+\/creation/g,
  [STEP_STOCKS]:
    /\/offre(\/((T-){0,1}[A-Z0-9]+))\/collectif(\/[A-Z,0-9]+)?\/stocks/g,
  [STEP_VISIBILITY]:
    /\/offre(\/([A-Z0-9]+))\/collectif(\/[A-Z,0-9]+)?\/visibilite/g,
  [STEP_RECAP]:
    /\/offre(\/((T-){0,1}[A-Z0-9]+))\/collectif(\/vitrine)?(\/[A-Z,0-9]+)?(\/creation)?\/recapitulatif/g,
  [STEP_CONFIRMATION]:
    /\/offre\/((T-){0,1}[A-Z0-9]+)\/collectif(\/vitrine)?(\/[A-Z,0-9]+)?\/confirmation/g,
  [STEP_PREVIEW]:
    /\/offre(\/((T-){0,1}[A-Z0-9]+))\/collectif(\/vitrine)?(\/[A-Z,0-9]+)?(\/creation)?\/apercu/g,
}

export const shouldBlockNavigation: BlockerFunction = ({
  currentLocation,
  nextLocation,
}) => {
  // when multiples url match (example: offer and stocks),
  // we're keeping the last one (example: stocks)
  let from
  const fromMatchs = Object.keys(collectiveUrlPatterns).filter(
    (stepName): boolean =>
      collectiveUrlPatterns[stepName]!.test(currentLocation.pathname)
  )
  if (fromMatchs.length) {
    from = fromMatchs.reverse()[0]
  }

  let to

  const toMatchs = Object.keys(collectiveUrlPatterns).filter(
    (stepName): boolean =>
      nextLocation.pathname.match(collectiveUrlPatterns[stepName]!) !== null
  )
  if (toMatchs.length) {
    to = toMatchs.reverse()[0]
  }
  // going back
  if (
    (from === STEP_STOCKS && to === STEP_OFFER) ||
    (from === STEP_STOCKS && to === STEP_OFFER_EDITION) ||
    (from === STEP_VISIBILITY && to === STEP_OFFER_EDITION) ||
    (from === STEP_VISIBILITY && to === STEP_STOCKS) ||
    (from === STEP_RECAP && to === STEP_VISIBILITY) ||
    (from === STEP_RECAP && to === STEP_STOCKS) ||
    (from === STEP_RECAP && to === STEP_OFFER_EDITION) ||
    (from === STEP_RECAP && to === STEP_OFFER) ||
    (from === STEP_RECAP && to === STEP_PREVIEW) ||
    (from === STEP_PREVIEW && to === STEP_OFFER_EDITION) ||
    (from === STEP_PREVIEW && to === STEP_RECAP)
  ) {
    return false
  }
  // going from confirmation to stock
  if (from === STEP_CONFIRMATION) {
    return false
  }
  if (
    // going to stocks
    to === STEP_STOCKS ||
    // or to visibility
    to === STEP_VISIBILITY ||
    // or to confirmation
    to === STEP_CONFIRMATION ||
    // or to recap
    to === STEP_RECAP ||
    // or from collective to individual or reverse
    (from === STEP_OFFER && to === STEP_OFFER) ||
    // or to preview
    to === STEP_PREVIEW
  ) {
    return false
  }

  if (
    from === STEP_RECAP &&
    nextLocation.pathname.startsWith('/remboursements/informations-bancaires')
  ) {
    return false
  }

  return true
}
