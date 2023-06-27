import { useAdapter } from 'hooks'

import { Offerer } from '../types'

import getOffererAdapter from './getOffererAdapter'

const useGetOfferer = (offererId?: string) =>
  useAdapter<Offerer, null>(() => getOffererAdapter(Number(offererId)))

export default useGetOfferer
