---
paths:
  - "**/*.ts"
  - "**/*.tsx"
  - "**/*.js"
  - "**/*.jsx"
---

# TypeScript Style Rules

- Use `const` over `let` unless reassignment is unavoidable
- Explicit return types on all exported functions
- Use `interface` over `type` for object shapes
- Avoid `any` -- use `unknown` with type guards or proper generics
- Use optional chaining (`?.`) over manual null checks
- All async functions must handle errors (try/catch or `.catch()`)
- `strict: true` in tsconfig -- no implicit any
