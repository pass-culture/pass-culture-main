import { apiAdage } from 'apiClient/api'
import { Adapter, AdapterFailure, Option } from 'pages/AdageIframe/app/types'

type GetAcademiesOptionsAdapter = Adapter<
  void,
  Option<string>[],
  Option<string>[]
>

const FAILING_RESPONSE: AdapterFailure<Option<string>[]> = {
  isOk: false,
  message: 'Nous avons rencontré un problème lors du chargemement des données',
  payload: [],
}

export const getAcademiesOptionsAdapter: GetAcademiesOptionsAdapter =
  async () => {
    try {
      const academies = await apiAdage.getAcademies()

      return {
        isOk: true,
        message: null,
        payload: academies.map(academy => ({
          value: academy,
          label: academy,
        })),
      }
    } catch (e) {
      return FAILING_RESPONSE
    }
  }
