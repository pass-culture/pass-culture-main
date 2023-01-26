import * as pcapiAdage from 'repository/pcapi/pcapiAdage'

import { Adapter, AdapterFailure, Option } from '../types'

type GetEducationalDomainsOptionsAdapter = Adapter<
  void,
  Option<number>[],
  Option<number>[]
>

const FAILING_RESPONSE: AdapterFailure<Option<number>[]> = {
  isOk: false,
  message: 'Nous avons rencontré un problème lors du chargemement des données',
  payload: [],
}

export const getEducationalDomainsOptionsAdapter: GetEducationalDomainsOptionsAdapter =
  async () => {
    try {
      const domains = await pcapiAdage.getEducationalDomains()

      return {
        isOk: true,
        message: null,
        payload: domains.map(({ id, name }) => ({ value: id, label: name })),
      }
    } catch (e) {
      return FAILING_RESPONSE
    }
  }
