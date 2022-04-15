import { RequestMock } from 'testcafe'

export const getSirenRequestMockAs = offerer => {
  const { address, city, latitude, longitude, name, postalCode, siren } =
    offerer
  return RequestMock()
    .onRequestTo(
      `https://entreprise.data.gouv.fr/api/sirene/v3/unites_legales/${siren}`
    )
    .respond(
      {
        unite_legale: {
          denomination: name,
          siren,
          etat_administratif: 'A',
          etablissement_siege: {
            etat_administratif: 'A',
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

export const getSirenRequestMockWithDefaultValues = () =>
  RequestMock()
    .onRequestTo(
      /\/entreprise.data.gouv.fr\/api\/sirene\/v3\/unites_legales\/.*/
    )
    .respond(
      {
        unite_legale: {
          id: 11654265,
          siren: '501106520',
          denomination: 'WEBEDIA',
          etat_administratif: 'A',
          etablissement_siege: {
            etat_administratif: 'A',
            code_postal: '92300',
            libelle_commune: 'LEVALLOIS-PERRET',
            enseigne_1: null,
            longitude: '2.276981',
            latitude: '48.893131',
            geo_l4: '2 RUE PAUL VAILLANT COUTURIER',
          },
        },
      },
      200,
      {
        'content-type': 'application/json; charset=utf-8',
        'access-control-allow-origin': '*',
      }
    )

export const getSirenRequestMockWithNoResult = () =>
  RequestMock()
    .onRequestTo(
      /\/entreprise.data.gouv.fr\/api\/sirene\/v3\/unites_legales\/.*/
    )
    .respond({}, 404, {
      'content-type': 'application/json; charset=utf-8',
      'access-control-allow-origin': '*',
    })
