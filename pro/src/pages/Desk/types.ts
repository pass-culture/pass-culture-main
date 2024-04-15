export enum MESSAGE_VARIANT {
  DEFAULT = 'default',
  ERROR = 'error',
}

export interface ErrorMessage {
  message: string
  variant: MESSAGE_VARIANT
}
