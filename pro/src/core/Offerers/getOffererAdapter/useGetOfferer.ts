import { useAdapter } from 'hooks'

import { IOfferer } from '../types'

import getOffererAdapter from './getOffererAdapter'

const useGetOfferer = (offererId?: string) =>
  useAdapter<IOfferer, null>(() => getOffererAdapter(offererId))

export default useGetOfferer
