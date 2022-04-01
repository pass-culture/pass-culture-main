import { default as originalCreateCachedSelector } from 're-reselect'
import { createSelector } from 'reselect'
import { IS_TEST } from 'utils/config'

export const createCachedSelector = IS_TEST
  ? createSelector
  : originalCreateCachedSelector
