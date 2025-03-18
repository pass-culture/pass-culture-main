export function getNationalProgramsForDomains(domains: string[]): number[] {
  for (const domain of domains) {
    nationalProgramsIds = new Set([
      domain.,
    ])
  }
  return Array.from(nationalProgramsIds)
}

// function getNationalProgramsForDomain(domain: string): number[] {
//   switch (domain) {
//     case '11': {
//       //  Univers du livre, de la lecture et des écritures -> Jeunes en librairie, Olympiade culturelle de PARIS 2024
//       return [6, 4]
//     }
//     case '6': {
//       //  Cinéma, audiovisuel -> Collège au cinéma, Lycéens et apprentis au cinéma, Olympiade culturelle de PARIS 2024
//       return [1, 3, 4]
//     }
//     default:
//       // Olympiade culturelle de PARIS 2024
//       return [4]
//   }
// }
