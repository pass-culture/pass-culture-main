type Error = {
  statusCode: number
  body: {
    code: string
  }
}

export const hasErrorCode = (error: any): error is Error =>
  typeof error?.body?.code === 'string'
