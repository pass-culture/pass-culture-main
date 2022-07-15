import {
  ALL_FRANCE_OPTION_LABEL,
  ALL_FRANCE_OPTION_VALUE,
  CULTURAL_PARTNER_OPTION_LABEL,
  CULTURAL_PARTNER_OPTION_VALUE,
  MAINLAND_OPTION_LABEL,
  MAINLAND_OPTION_VALUE,
  domtomOptions,
  interventionOptions,
} from 'core/Venue'

export const getInterventionAreaLabels = (
  interventionArea: string[]
): string => {
  const labels = []
  if (interventionArea.includes(CULTURAL_PARTNER_OPTION_VALUE)) {
    labels.push(CULTURAL_PARTNER_OPTION_LABEL)
  }

  if (interventionArea.includes(ALL_FRANCE_OPTION_VALUE)) {
    labels.push(ALL_FRANCE_OPTION_LABEL)
  } else if (interventionArea.includes(MAINLAND_OPTION_VALUE)) {
    labels.push(MAINLAND_OPTION_LABEL)

    domtomOptions.forEach(domtomOption => {
      if (interventionArea.includes(domtomOption.value.toString())) {
        labels.push(domtomOption.label)
      }
    })
  }

  if (labels.length === 0) {
    interventionOptions.forEach(interventionOption => {
      if (interventionArea.includes(interventionOption.value.toString())) {
        labels.push(interventionOption.label)
      }
    })
  }

  return labels.join(', ')
}
