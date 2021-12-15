export const getErrorMessage = (error: any): string => {
    if (Object.keys(error.errors).includes('educationalInstitution')){
        return 'Votre établissement n’a pas de budget alloué pour cette année scolaire.'
    }
    return 'Impossible de préréserver cette offre.\nVeuillez contacter le support'
}
