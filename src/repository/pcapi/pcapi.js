import { client } from "repository/pcapi/pcapiClient"

export const authenticate = async () => {
  return client.get("/authenticate")
}
