type Error = {
  statusCode: number
  content: {
    code: string
  }
}

export const hasErrorCode = (error: any): error is Error =>
  typeof error?.content?.code === 'string'
