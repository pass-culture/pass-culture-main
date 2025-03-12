export enum MESSAGE_VARIANT {
  DEFAULT = 'default',
  ERROR = 'error',
  SUCCESS = 'success',
}

export interface ErrorMessage {
  message: string
  variant?: MESSAGE_VARIANT
}
