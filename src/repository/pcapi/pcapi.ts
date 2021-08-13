import { client } from "repository/pcapi/pcapiClient"

export const authenticate = async (): Promise<void> => {
  return client.get("/authenticate")
}
