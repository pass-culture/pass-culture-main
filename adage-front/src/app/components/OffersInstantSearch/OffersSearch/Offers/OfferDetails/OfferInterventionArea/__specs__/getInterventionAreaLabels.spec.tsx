import { getInterventionAreaLabels } from '../OfferInterventionArea'

describe('getInterventionAreaLabels', () => {
  it('should format intervention area when there are a few departments', () => {
    const interventionArea = ['30', '75', '92']
    expect(getInterventionAreaLabels(interventionArea)).toStrictEqual(
      'Gard (30) - Paris (75) - Hauts-de-Seine (92)'
    )
  })

  it('should format intervention area when all france option is selected', () => {
    const interventionArea = ['all', '75', '92']
    expect(getInterventionAreaLabels(interventionArea)).toStrictEqual(
      'France métropolitaine et d’outre-mer'
    )
  })

  it('should format intervention area when mainland option is selected + domtom departments', () => {
    const interventionArea = ['mainland', '971']
    expect(getInterventionAreaLabels(interventionArea)).toStrictEqual(
      'France métropolitaine - Guadeloupe (971)'
    )
  })
})
