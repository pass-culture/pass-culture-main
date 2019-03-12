module.exports = {
  collectCoverageFrom: [
    // "**/*.{js,jsx}",
    '<rootDir>/src/**.{js,jsx,mjs}',
    // "!**/node_modules/**",
    '!<rootDir>/node_modules/',
    '!<rootDir>/build/',
  ],
  moduleFileExtensions: [
    'web.js',
    'mjs',
    'js',
    'json',
    'web.jsx',
    'jsx',
    'node',
  ],
  moduleNameMapper: {
    '^react-native$': 'react-native-web',
  },
  setupFiles: ['<rootDir>/jest-polyfill.js', '<rootDir>/jest.setup.js'],
  testEnvironment: 'node',
  testMatch: [
    '<rootDir>/src/**/__tests__/**/*.{js,jsx,mjs}',
    '<rootDir>/src/**/?(*.)(spec|test).{js,jsx,mjs}',
    '**/?(*.)+(spec).js?(x)',
  ],
  testURL: 'http://localhost',
  transform: {
    '^.+\\.(js|jsx|mjs)$': '<rootDir>/node_modules/babel-jest',
    '^.+\\.js$': 'babel-jest',
  },
  transformIgnorePatterns: [
    '<rootDir>/node_modules/',
    '[/\\\\]node_modules[/\\\\].+\\.(js|jsx|mjs)$',
  ],
  verbose: true,
}
