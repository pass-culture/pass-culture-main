import { createSlice, PayloadAction } from '@reduxjs/toolkit'

import { NotificationTypeEnum } from '@/commons/hooks/useNotification'

export interface Notification {
  text: string | null
  type: NotificationTypeEnum
  duration?: number
}

export interface NotificationState {
  isStickyBarOpen: boolean
  notification: Notification | null
}

export const initialState: NotificationState = {
  isStickyBarOpen: false,
  notification: null,
}

const notificationsSlice = createSlice({
  name: 'notifications',
  initialState,
  reducers: {
    showNotification: (
      state: NotificationState,
      action: PayloadAction<Notification>
    ) => {
      state.notification = action.payload
    },
    closeNotification: (state: NotificationState) => {
      state.notification = null
    },
    setIsStickyBarOpen: (
      state: NotificationState,
      action: PayloadAction<boolean>
    ) => {
      state.isStickyBarOpen = action.payload
    },
  },
})

export const notificationsReducer = notificationsSlice.reducer

export const { showNotification, closeNotification, setIsStickyBarOpen } =
  notificationsSlice.actions
