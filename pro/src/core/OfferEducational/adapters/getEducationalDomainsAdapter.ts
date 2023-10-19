import { api } from 'apiClient/api'
import { GET_DATA_ERROR_MESSAGE } from 'core/shared'
import { SelectOption } from 'custom_types/form'

export type GetEducationalDomainsAdapter = Adapter<
  void,
  SelectOption[],
  SelectOption[]
>

const FAILING_RESPONSE: AdapterFailure<SelectOption[]> = {
  isOk: false,
  message: GET_DATA_ERROR_MESSAGE,
  payload: [],
}

export const getEducationalDomainsAdapter: GetEducationalDomainsAdapter =
  async () => {
    try {
      const domains = await api.listEducationalDomains()

      return {
        isOk: true,
        message: null,
        payload: domains.map((domain) => ({
          value: domain.id.toString(),
          label: domain.name,
        })),
      }
    } catch (e) {
      return FAILING_RESPONSE
    }
  }
