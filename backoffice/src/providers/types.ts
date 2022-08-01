export type AuthToken = {
  sub: string
  name: string
  picture: string
}

export type tokenApiPayload = {
  email: string
  perms: string[]
  exp: number
}
