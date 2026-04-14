# SchoolLinux Frontend: Technical Documentation

## Stack and build system
- **Language**: TypeScript
- **UI framework**: React 19
- **Bundler/dev server**: Vite 8
- **HTTP client**: Axios
- **Realtime**: `socket.io-client` (websocket transport)
- **Table UI**: `react-data-grid`
- **Icons**: Font Awesome React packages
- **Notifications**: `@brenoroosevelt/toast`

Build command (root): `npm run build` (`tsc -b && vite build`), output goes to `frontend/dist`.

## Frontend folder structure
- `frontend/main.tsx`: app bootstrap and provider composition
- `frontend/App.tsx`: top-level role switcher (Teacher vs Student)
- `frontend/api/*`: typed API and socket adapters
- `frontend/contexts/*`: global async state containers
- `frontend/views/*`: role-specific UI screens
- `frontend/types/*`: shared request/response/event types
- `frontend/helpers/*`: error normalization and toast wrappers
- `frontend/config/env.ts`: runtime environment and mock-preview mode
- `frontend/styles/*`, `index.css`, `App.css`: global and screen-specific styles

## Rendering and provider graph
`main.tsx` renders to `document.body` in `StrictMode`, nesting providers in this order:
1. `UserProvider`
2. `GameProvider`
3. `UsersProvider`
4. `ExtendedGameProvider`
5. `App`

This layering matters because:
- `UsersProvider` and `ExtendedGameProvider` read role info from `UserContext`.
- `App` uses `UserContext` to choose Teacher or Student UI.

## Environment and runtime config (`frontend/config/env.ts`)

### API base URL
- Default: `http://${location.hostname}:8000`
- Override via `VITE_API_BASE_URL`

### Mock preview mode
- Controlled by `VITE_MOCK_PREVIEW` + optional `VITE_MOCK_SCREEN`
- Screens: `"student-login" | "student-content" | "teacher"`
- Injects fake student, users map, current game, games list, and game state
- `getMockUserResponse()` returns role/session shape expected by `UserContext`

This mode bypasses network calls in contexts and uses static in-memory data.

## API layer

### Base clients (`frontend/api/api.ts`)
- Axios instance:
  - `baseURL: ${apiBaseUrl}/`
  - 10s timeout
  - JSON content type
- Socket client:
  - `io(apiBaseUrl, { autoConnect: true, transports: ["websocket"] })`

### HTTP modules
- `health.ts`: `ping()` -> `"pong"`
- `user.ts`:
  - `registerUser`
  - `getCurrentUser`
  - `getAllUsers`
  - `setUserKicked(ip, kicked)`
  - `deleteCurrentUser`
- `game.ts`:
  - `getCurrentGame`
  - `listGames`
  - `setCurrentGame`
  - `getGameState`
  - `startGame`
  - `stopGame`
  - `checkGame(submission = "")`

Notes from code comments:
- `/game/start` and `/game/stop` are treated as void responses.
- `/game/check` may return empty body; frontend maps this to `null`.

### Socket module (`frontend/api/socket.ts`)
- `typedSocket` casts raw socket to typed events interface.
- Utility wrappers:
  - `connectSocket`, `disconnectSocket`
  - `onSocketEvent(event, handler)` returns unsubscribe callback
  - `offSocketEvent`

## Type system

### User types (`frontend/types/user.ts`)
- `RegisterRequest`: `{ name, pcName }`
- `SafeUserData`: `{ name, pcName, score, kicked }`
- `UserResponse`: `{ isTeacher, user }`
- `UsersMap`: `Record<string, SafeUserData>` keyed by IP
- `KickedEventPayload`: `{ kicked }`

### Game types (`frontend/types/game.ts`)
- Setting type union: `string | number | boolean | option`
- `GameSettingsItem`: `{ name, type, options, default, value }`
- `GameResponseSafe`: student-visible game payload
- `GameResponse`: safe payload + `anticheatRequired`, `settingsForm`
- `GameChangeRequest`: `{ gameKey, settings? }`

### Socket event types (`frontend/types/socket.ts`)
Server-to-client events:
- `users_update(users)`
- `kicked({ kicked })`
- `game_change(game)`
- `game_state_changed({ state: "idle" | "init" | "running" })`

Client-to-server event map is currently empty (reserved for future use).

## Global contexts and data flow

### `UserContext`
State:
- `user: UserResponse | null`
- `loading`, `error`

Behavior:
- On mount: fetches `/user/me` (or mock response)
- Subscribes to socket `kicked` and updates `user.user.kicked` in-place
- Exposes `refetch()` for explicit reloads (used after register/delete/check actions)

### `GameContext`
State:
- `game: GameResponseSafe | null`
- `gameState: "idle" | "init" | "running"`
- `loading`, `error`

Behavior:
- On mount: parallel fetch of `/game/` + `/game/state`
- Subscribes to:
  - `game_change` to refresh current safe game metadata
  - `game_state_changed` to track lifecycle state

### `UsersContext` (teacher roster)
State:
- `users: UsersMap | null`
- `loading`, `error`

Behavior:
- Active only for teacher sessions
- Fetches `/user/all`
- Subscribes to `users_update` socket event for realtime roster/score refresh
- Exposes optimistic local kicked toggle helper `updateUserKicked`

### `ExtendedGameContext` (teacher game management)
State:
- `currentGame: GameResponse | null`
- `gamesList: Record<string, GameResponse> | null`
- `loading`, `error`

Behavior:
- Fetches current game for all roles
- Fetches games catalog only for teacher role
- Provides `setCurrentGame(gameKey, settings?)` that sends `GameChangeRequest`
- In mock mode updates local state without network

## Top-level app switch (`frontend/App.tsx`)
- Shows loading spinner while user context is loading.
- Renders:
  - `<Teacher />` when `user.isTeacher === true`
  - `<Student />` otherwise
- Always displays header and footer.

## Student UX

### `views/Student.tsx`
- If not registered (`user === null` or `user.user === null`): shows login form
- Login flow:
  1. calls `registerUser({ pcName, name })`
  2. calls `refetch()` from `UserContext`
- Logout flow:
  1. confirmation dialog
  2. `deleteCurrentUser()`
  3. `refetch()`

### `views/StudentLoginForm.tsx`
- Controlled form for `pcName` and `name`
- Enforces non-empty trimmed values before submit
- Shows loading status while backend verifies connectivity/registers

### `views/StudentContent.tsx`
- Displays student identity + score
- Reads game + lifecycle state from `GameContext`
- Submission gating rules:
  - no game -> no submission
  - string game requires non-empty answer
  - kicked users blocked
  - game must be in `"running"` state
- Submission behavior:
  - string game sends trimmed answer
  - non-string game sends empty payload (SSH check done backend-side)
  - after submit, refetches user profile to refresh score/kicked state

## Teacher UX (`views/Teacher.tsx`)

### Student table
- Uses `react-data-grid` with sortable columns:
  - IP, computer name, student name, score, action
- Local sorting supports multi-sort (`SortColumn[]`)
- Action column renders kick/restore button via `ActionFormatter`

### Kick/restore behavior
- Optimistic UI update through `updateUserKicked`
- API call `setUserKicked(ip, bool)`
- On failure, reverts optimistic update and shows toast
- Buttons are disabled while game is running

### Game selection and settings
- Game selector is populated from `gamesList` (`ExtendedGameContext`)
- Switching game clears pending unsaved `settingsChanges`
- Settings editor dynamically renders per `currentGame.settingsForm`:
  - checkbox for boolean
  - number input for number
  - select for option
  - text for string
- `Apply settings` sends only changed keys via `setCurrentGame(gameKey, settingsChanges)`

### Start/stop controls
- `startGame()` / `stopGame()` API calls with loading state
- UI disables actions depending on `gameState`
- Local status badge reflects `idle/init/running`
- Handles backend `409` responses with warning toasts

## Helper modules
- `helpers/error.ts`: `toError(unknown)` normalizer
- `helpers/notify.ts`: centralized toast wrappers (`success/info/warning/error`) with shared placement/duration defaults

## Styling architecture
- `index.css`: global theme variables, layout shell, header/footer, scrollbar/selection, base animation
- `App.css`: shared main-area styles, loading view spinner, common heading/error banner styles
- `styles/student.css`: login/content layouts, forms, score panel, submission area, logout button, responsive behavior
- `styles/teacher.css`: data-grid theming overrides, kick/restore button styles, settings form controls, game controls, responsive table tweaks

Design language is dark UI with green accent palette (`--accent`, `--accent-strong`) shared across views.

## HTML entry and env typing
- `frontend/index.html` loads `main.tsx` as module script and sets `lang="ru"`.
- `frontend/vite-env.d.ts` augments `ImportMetaEnv` with all supported `VITE_*` keys for type-safe env access.

## Runtime behavior summary
- Role is resolved from backend `/user/me` and drives entire app branch.
- Most teacher updates are realtime via socket (`users_update`, `game_change`, `game_state_changed`).
- Student kicked state is realtime via socket `kicked`.
- Contexts own fetch + subscribe lifecycle and expose refetch methods for explicit synchronization after mutating actions.

## Integration expectations with backend
- Backend returns camelCase JSON; frontend types are camelCase and map directly.
- Teacher permissions are backend-enforced; frontend still hides/locks inappropriate actions.
- Socket event payloads are assumed to match `ServerToClientEvents` contracts exactly.
