export const MOCKED_BACK_ADDRESS_STREET = '3 RUE DE VALOIS'
export const MOCKED_BACK_ADDRESS_LABEL = '3 Rue de Valois 75001 Paris'
export const DEFAULT_AXE_CONFIG = {
  axeCorePath: './node_modules/axe-core/axe.min.js',
}
//  TODO : Fix the "unaccessible" link axe-core error, cf this WIP :
//  https://www.notion.so/passcultureapp/Redirection-SPA-d-claration-de-titres-de-niveau-1-et-skip-links-94461d27b2444ed29b5103ea3d0ede2e
export const DEFAULT_AXE_RULES = { rules: { 'link-name': { enabled: false } } }
