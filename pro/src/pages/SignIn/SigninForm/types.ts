export interface ISigninFormValues {
  email: string
  password: string
}

export interface ISigninApiErrorResponse {
  status: number
  errors: {
    [key: string]: string
  }
}
