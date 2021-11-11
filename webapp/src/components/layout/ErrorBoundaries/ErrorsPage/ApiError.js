export class ApiError {
  constructor(httpCode = 0) {
    this.httpCode = httpCode
  }
}
