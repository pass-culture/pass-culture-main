import { ELIGIBLE, SOON, TOO_OLD, TOO_YOUNG } from '../domain/checkIfAgeIsEligible'

export const eligibilityPaths = {
  [ELIGIBLE]: 'eligible',
  [TOO_OLD]: 'pas-eligible',
  [TOO_YOUNG]: 'trop-tot',
  [SOON]: 'bientot',
}
