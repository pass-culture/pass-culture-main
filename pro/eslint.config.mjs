import typescriptEslint from "@typescript-eslint/eslint-plugin";
import globals from "globals";
import tsParser from "@typescript-eslint/parser";
import path from "node:path";
import { fileURLToPath } from "node:url";
import js from "@eslint/js";
import importPlugin from 'eslint-plugin-import';
import reactHook from 'eslint-plugin-react-hooks';
import react from 'eslint-plugin-react';
import eslintPluginPrettierRecommended from "eslint-plugin-prettier/recommended";
import pluginCypress from 'eslint-plugin-cypress/flat'

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

export default [  js.configs.recommended,
    importPlugin.flatConfigs.recommended,
    eslintPluginPrettierRecommended,
    pluginCypress.configs.recommended,
    { 
        ignores: [
        "src/api/v1/gen/*",
        "src/api/v2/gen/*",
        "**/*.svg",
        "**/*.scss",
        "**/*.md",
        "**/*.mdx",
        "**/*.jpg",
        "**/*.png",
        "src/index.html",
        "**/.eslintrc.cjs",
        "src/**/*.gif",
    ],
  }, {
    
    plugins: {
        "react": react, 
        "react-hooks": reactHook, 
        "@typescript-eslint": typescriptEslint,
        "cypress": pluginCypress
    },

    languageOptions: {
        globals: {
            ...globals.browser,
            ...globals.jest,
            ...globals.node,
        },

        parser: tsParser,
        ecmaVersion: 6,
        sourceType: "module",

        parserOptions: {
            project: ["./tsconfig.json"],
            tsconfigRootDir: __dirname,
        },
    },

    settings: {
        react: {
            version: "detect",
        },

        "import/resolver": {
            node: {
                extensions: [".ts", ".tsx"],
                paths: ["."],
                moduleDirectory: ["node_modules", "src"],
            },
        },
    },

    rules: {
        "react-hooks/rules-of-hooks": "error",
        "react-hooks/exhaustive-deps": "warn",
        'no-unused-vars': 'off',
        'import/no-dynamic-require': 'warn',
        'import/no-nodejs-modules': 'warn',
        "import/no-unresolved": 0,
        "import/named": 0,
        curly: ["error", "all"],
        "no-console": 1,

        "import/order": ["warn", {
            groups: ["builtin", "external", "internal", "parent", "sibling", "index"],
            "newlines-between": "always",

            alphabetize: {
                order: "asc",
                caseInsensitive: true,
            },
        }],

        "@typescript-eslint/ban-ts-comment": "off",
        "@typescript-eslint/no-explicit-any": "off",
        "@typescript-eslint/no-empty-function": "off",
        "react/react-in-jsx-scope": "off",
        "@typescript-eslint/prefer-ts-expect-error": "error",

        "react/no-unescaped-entities": ["error", {
            forbid: [{
                char: "'",
                alternatives: ["’"],
            }],
        }],

        eqeqeq: "error",
        "require-await": "error",
        "import/no-named-as-default": "error",
        "import/no-default-export": "error",
        "@typescript-eslint/await-thenable": "error",
        "react/prop-types": "error",
        "@typescript-eslint/prefer-string-starts-ends-with": "error",
        "@typescript-eslint/no-restricted-types": "error",
        "@typescript-eslint/no-empty-object-type": "error",
        "@typescript-eslint/no-unsafe-function-type": "error",
        "@typescript-eslint/no-wrapper-object-types": "error",
        "@typescript-eslint/switch-exhaustiveness-check": "error",
        "@typescript-eslint/no-unnecessary-type-arguments": "error",
        "@typescript-eslint/no-unnecessary-boolean-literal-compare": "error",
        "@typescript-eslint/no-floating-promises": "error",
        "@typescript-eslint/no-unnecessary-condition": "error",

        "react/self-closing-comp": ["error", {
            component: true,
            html: true,
        }],

        "@typescript-eslint/naming-convention": ["error", {
            selector: "typeAlias",
            format: ["PascalCase"],
        }],

        "react-hooks/exhaustive-deps": "warn",
        "prettier/prettier": [
            "error",
            {
                "usePrettierrc": true
              }
          ]
    },
}, {
    files: ["**/*.stories.tsx"],

    rules: {
        "import/no-default-export": "off",
    },
}, {
    files: ["cypress/**/*.ts"],

    languageOptions: {
        ecmaVersion: 6,
        sourceType: "module",

        parserOptions: {
            project: ["cypress/tsconfig.json"],
            tsconfigRootDir: __dirname,
        },
    },
}];