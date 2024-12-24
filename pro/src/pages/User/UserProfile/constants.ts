import { type EnumType } from 'commons/custom_types/utils'

export const Forms = {
  USER_IDENTITY: 0,
  USER_PHONE: 1,
  USER_EMAIL: 2,
  USER_PASSWORD: 3,
} as const
// eslint-disable-next-line no-redeclare
export type Forms = EnumType<typeof Forms>
