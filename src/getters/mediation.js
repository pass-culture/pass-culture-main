import get from 'lodash.get'

export default function getMediation(recommendation) {
  return get(recommendation, 'mediation')
}
