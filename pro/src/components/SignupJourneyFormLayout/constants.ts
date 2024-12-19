import { type EnumType } from 'commons/custom_types/utils'

export const OnboardingFormNavigationAction = {
  Breadcrumb: 'Breadcrumb',
  ActionBar: 'ActionBar',
  NewOfferer: 'NewOfferer',
  UpdateFromValidation: 'UpdateFromValidation',
  JoinModal: 'JoinModal',
  WaitingLinkButton: 'WaitingLinkButton',
  LinkModalActionButton: 'LinkModalActionButton',
} as const
// eslint-disable-next-line no-redeclare
export type OnboardingFormNavigationAction = EnumType<
  typeof OnboardingFormNavigationAction
>
