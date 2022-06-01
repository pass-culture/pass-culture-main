import * as pcapi from 'repository/pcapi/pcapi'

import { SelectOption } from 'custom_types/form'

type GetEducationalDomainsAdapter = Adapter<
  void,
  SelectOption[],
  SelectOption[]
>

const FAILING_RESPONSE: AdapterFailure<SelectOption[]> = {
  isOk: false,
  message: 'Nous avons rencontré un problème lors du chargemement des données',
  payload: [],
}

export const getEducationalDomainsAdapter: GetEducationalDomainsAdapter =
  async () => {
    try {
      const domains = await pcapi.getEducationalDomains()

      return {
        isOk: true,
        message: null,
        payload: domains.map(domain => ({
          value: domain.id.toString(),
          label: domain.name,
        })),
      }
    } catch (e) {
      return FAILING_RESPONSE
    }
  }
