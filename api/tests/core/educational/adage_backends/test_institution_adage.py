import pytest

from pcapi.core.educational.adage_backends.serialize import AdageEducationalInstitution
from pcapi.core.educational.api.institution import synchronise_adage_and_institution
from pcapi.core.educational.factories import EducationalInstitutionFactory


@pytest.mark.usefixtures("db_session")
class ReturnSuccessTest:
    def test_synchronise_educational_institution_from_adage(self, client):
        # GIVEN
        institution_1 = EducationalInstitutionFactory(institutionId="1", isActive=True)
        institution_2 = EducationalInstitutionFactory(institutionId="2", isActive=False)
        institution_3 = EducationalInstitutionFactory(institutionId="3", isActive=True)
        institution_4 = EducationalInstitutionFactory(institutionId="4", isActive=False)
        institution_5 = EducationalInstitutionFactory(institutionId="5", isActive=True)
        institution_6 = EducationalInstitutionFactory(institutionId="6", isActive=False)

        adage_institution_1 = AdageEducationalInstitution(
            uai="1",
            sigle="CLG",
            libelle="DE LA TOUR0",
            communeLibelle="PARIS",
            courriel="contact+collegelatour@example.com",
            telephone="0600000000",
            codePostal="75000",
        )
        adage_institution_2 = AdageEducationalInstitution(
            uai="2",
            sigle="CLG",
            libelle="DE LA TOUR0",
            communeLibelle="PARIS",
            courriel="contact+collegelatour@example.com",
            telephone="0600000000",
            codePostal="75000",
        )
        adage_institution_3 = AdageEducationalInstitution(
            uai="3",
            sigle="ECGT PR",
            libelle="Poudlard",
            communeLibelle="somewhere",
            courriel="dumbledor@example.com",
            telephone="0102030405",
            codePostal="75001",
        )
        adage_institution_4 = AdageEducationalInstitution(
            uai="4",
            sigle="ECGT PR",
            libelle="Poudlard",
            communeLibelle="somewhere",
            courriel="dumbledor@example.com",
            telephone="0102030405",
            codePostal="75001",
        )
        adage_institutions = [adage_institution_1, adage_institution_2, adage_institution_3, adage_institution_4]
        institutions = [institution_1, institution_2, institution_3, institution_4, institution_5, institution_6]

        # WHEN
        synchronise_adage_and_institution(adage_institutions=adage_institutions, institutions=institutions)

        # THEN
        assert institution_1.institutionId == adage_institution_1.uai
        assert institution_1.name == adage_institution_1.libelle
        assert institution_1.city == adage_institution_1.communeLibelle
        assert institution_1.institutionType == "COLLEGE"
        assert institution_1.postalCode == adage_institution_1.codePostal
        assert institution_1.email == adage_institution_1.courriel
        assert institution_1.phoneNumber == adage_institution_1.telephone
        assert institution_1.isActive is True

        assert institution_2.institutionId == adage_institution_2.uai
        assert institution_2.name == adage_institution_2.libelle
        assert institution_2.city == adage_institution_2.communeLibelle
        assert institution_2.institutionType == "COLLEGE"
        assert institution_2.postalCode == adage_institution_2.codePostal
        assert institution_2.email == adage_institution_2.courriel
        assert institution_2.phoneNumber == adage_institution_2.telephone
        assert institution_2.isActive is True

        assert institution_3.institutionId == adage_institution_3.uai
        assert institution_3.name == adage_institution_3.libelle
        assert institution_3.city == adage_institution_3.communeLibelle
        assert institution_3.institutionType == "ECOLE GENERALE ET TECHNOLOGIQUE PRIVEE"
        assert institution_3.postalCode == adage_institution_3.codePostal
        assert institution_3.email == adage_institution_3.courriel
        assert institution_3.phoneNumber == adage_institution_3.telephone
        assert institution_3.isActive is True

        assert institution_4.institutionId == adage_institution_4.uai
        assert institution_4.name == adage_institution_4.libelle
        assert institution_4.city == adage_institution_4.communeLibelle
        assert institution_4.institutionType == "ECOLE GENERALE ET TECHNOLOGIQUE PRIVEE"
        assert institution_4.postalCode == adage_institution_4.codePostal
        assert institution_4.email == adage_institution_4.courriel
        assert institution_4.phoneNumber == adage_institution_4.telephone
        assert institution_4.isActive is True

        assert institution_5.isActive is False
        assert institution_6.isActive is False
