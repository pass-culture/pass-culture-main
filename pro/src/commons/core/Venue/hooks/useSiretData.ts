import useSWRMutation from 'swr/mutation'

import {
  CHECK_SIRET_QUERY_KEY,
  GET_SIRET_DATA_QUERY_KEY,
} from '@/commons/config/swrQueryKeys'

import { checkSiret, getSiretData } from '../utils/getSiretData'

export const useGetSiretData = () => {
  const { trigger } = useSWRMutation(
    GET_SIRET_DATA_QUERY_KEY,
    (_key: string, { arg }: { arg: string }) => getSiretData(arg)
  )

  return trigger
}

export const useCheckSiret = () => {
  const { trigger } = useSWRMutation(
    CHECK_SIRET_QUERY_KEY,
    (_key: string, { arg }: { arg: string }) => checkSiret(arg)
  )

  return trigger
}
