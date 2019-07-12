import { RequestMock } from 'testcafe'

export const getSirenRequestMockAs = offerer => {
  const { address, city, latitude, longitude, name, postalCode, siren } = offerer
  return RequestMock()
    .onRequestTo(`https://sirene.entreprise.api.gouv.fr/v1/siren/${siren}`)
    .respond(
      {
        siege_social: {
          siren,
          l1_normalisee: name,
          l4_normalisee: address,
          libelle_commune: city,
          latitude: latitude,
          longitude: longitude,
          code_postal: postalCode,
        },
      },
      200,
      { 'access-control-allow-origin': '*' }
    )
}

export const getSiretRequestMockAs = venue => {
  const { address, city, latitude, longitude, name, postalCode, siret } = venue
  return RequestMock()
    .onRequestTo(`https://sirene.entreprise.api.gouv.fr/v1/siret/${siret}`)
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
