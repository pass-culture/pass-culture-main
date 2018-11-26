module.exports = {
  collectCoverageFrom: [
    // "**/*.{js,jsx}",
    '<rootDir>/src/**.{js,jsx}',
    // "!**/node_modules/**",
    '!<rootDir>/node_modules/',
    '!<rootDir>/build/',
  ],

  setupFiles: ['<rootDir>/jest-polyfill.js', '<rootDir>/jest.setup.js'],
  testEnvironment: 'node',
  testMatch: ['**/?(*.)+(spec).js?(x)'],
  testURL: 'http://localhost',
  transform: {
    '^.+\\.js$': 'babel-jest',
  },
  transformIgnorePatterns: [
    '<rootDir>/node_modules/',
    '[/\\\\]node_modules[/\\\\].+\\.(js|jsx|mjs)$',
  ],
  verbose: true,
}
