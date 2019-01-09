import get from 'lodash.get'

const getRouterParamByKey = (reactRouterMatch, stringkey) => {
  if (!reactRouterMatch || !stringkey) {
    throw new Error('getRouterParamByKey: Missing arguments')
  }
  const token = get(reactRouterMatch, `params.${stringkey}`) || undefined
  return token
}

export default getRouterParamByKey
