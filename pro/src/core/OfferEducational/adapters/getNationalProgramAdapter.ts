import { api } from 'apiClient/api'
import { GET_DATA_ERROR_MESSAGE } from 'core/shared'
import { SelectOption } from 'custom_types/form'

type GetNationalProgramsAdapter = Adapter<void, SelectOption[], SelectOption[]>

const FAILING_RESPONSE = {
  isOk: false,
  message: GET_DATA_ERROR_MESSAGE,
  payload: [],
}

export const getNationalProgramsAdapter: GetNationalProgramsAdapter =
  async () => {
    try {
      const result = await api.getNationalPrograms()

      return {
        isOk: true,
        message: null,
        payload: result.map(nationalProgram => ({
          label: nationalProgram.name,
          value: nationalProgram.id,
        })),
      }
    } catch (e) {
      return FAILING_RESPONSE
    }
  }
