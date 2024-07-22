import {
  ALL_FRANCE_OPTION_VALUE,
  MAINLAND_OPTION_VALUE,
  departmentLabelByValue,
  departmentOptions,
  domtomOptions,
} from 'pages/AdageIframe/app/constants/departmentOptions'

export const getInterventionAreaLabelsToDisplay = (
  interventionArea: string[]
): string[] => {
  const labels: string[] = []

  if (
    (interventionArea.includes(MAINLAND_OPTION_VALUE) ||
      interventionArea.includes(ALL_FRANCE_OPTION_VALUE)) &&
    departmentLabelByValue[MAINLAND_OPTION_VALUE]
  ) {
    labels.push(departmentLabelByValue[MAINLAND_OPTION_VALUE])

    domtomOptions.forEach((domtomOption) => {
      if (interventionArea.includes(domtomOption.value.toString())) {
        const [departmentCode, departmentLabel] =
          domtomOption.label.split(' - ')
        labels.push(`${departmentLabel} (${departmentCode})`)
      }
    })

    return labels
  }

  departmentOptions.forEach((interventionOption) => {
    if (interventionArea.includes(interventionOption.value.toString())) {
      const [departmentCode, departmentLabel] =
        interventionOption.label.split(' - ')
      labels.push(`${departmentLabel} (${departmentCode})`)
    }
  })

  return labels
}

export function getInterventionAreaLabels(interventionAreas: string[]): string {
  return getInterventionAreaLabelsToDisplay(interventionAreas).join(` - `)
}
