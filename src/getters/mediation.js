import get from 'lodash.get'

export default function getMediation (userMediation) {
  return get(userMediation, 'mediation')
}
