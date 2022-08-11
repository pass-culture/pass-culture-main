import { RequestMock } from 'testcafe'

export const getSiretRequestMockAs = venue => {
  const { address, city, latitude, longitude, name, postalCode, siret } = venue
  return RequestMock()
    .onRequestTo(
      `https://entreprise.data.gouv.fr/api/sirene/v3/etablissements/${siret}`
    )
    .respond(
      {
        etat_administratif: 'A',
        etablissement: {
          etat_administratif: 'A',
          code_postal: postalCode,
          enseigne_1: name,
          geo_l4: address,
          libelle_commune: city,
          latitude: latitude,
          longitude: longitude,
          siret: siret,
          unite_legale: {
            etat_administratif: 'A',
          },
        },
      },
      200,
      { 'access-control-allow-origin': '*' }
    )
}

export const getSirenRequestMockWithNoResult = () =>
  RequestMock()
    .onRequestTo(
      /\/entreprise.data.gouv.fr\/api\/sirene\/v3\/unites_legales\/.*/
    )
    .respond({}, 404, {
      'content-type': 'application/json; charset=utf-8',
      'access-control-allow-origin': '*',
    })
