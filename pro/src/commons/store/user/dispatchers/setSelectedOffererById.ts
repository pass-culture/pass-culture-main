import { createAsyncThunk } from '@reduxjs/toolkit'

import type { AppThunkApiConfig } from '../../store'

// TODO (igabriele, 2026-04-20): Delete this dispatcher once `WIP_SWITCH_VENUE` FF is removed.
export const setSelectedOffererById = createAsyncThunk<
  string,
  // biome-ignore lint/suspicious/noExplicitAny: For refactoring purpose
  any,
  AppThunkApiConfig
>('user/setSelectedOffererById', async () => {
  return await Promise.resolve('')
})
