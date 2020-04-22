import { RequestMock } from 'testcafe'

export const getSirenRequestMockAs = offerer => {
  const { address, city, latitude, longitude, name, postalCode, siren } = offerer
  return RequestMock()
    .onRequestTo(`https://entreprise.data.gouv.fr/api/sirene/v3/unites_legales/${siren}`)
    .respond(
      {
        unite_legale: {
          denomination: name,
          siren,
          etablissement_siege: {
            geo_l4: address,
            libelle_commune: city,
            latitude: latitude,
            longitude: longitude,
            code_postal: postalCode,
          },
        },
      },
      200,
      { 'access-control-allow-origin': '*' }
    )
}

export const getSiretRequestMockAs = venue => {
  const { address, city, latitude, longitude, name, postalCode, siret } = venue
  return RequestMock()
    .onRequestTo(`https://entreprise.data.gouv.fr/api/sirene/v1/siret/${siret}`)
    .respond(
      {
        etablissement: {
          code_postal: postalCode,
          l1_normalisee: name,
          l4_normalisee: address,
          libelle_commune: city,
          latitude: latitude,
          longitude: longitude,
          siret: siret,
        },
      },
      200,
      { 'access-control-allow-origin': '*' }
    )
}
