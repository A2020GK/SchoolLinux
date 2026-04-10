/// <reference types="vite/client" />

interface ImportMetaEnv {
    readonly VITE_API_BASE_URL?: string;
    readonly VITE_MOCK_PREVIEW?: string;
    readonly VITE_MOCK_SCREEN?: "student-login" | "student-content" | "teacher";
    readonly VITE_MOCK_STUDENT_NAME?: string;
    readonly VITE_MOCK_STUDENT_PC?: string;
    readonly VITE_MOCK_STUDENT_SCORE?: string;
}

interface ImportMeta {
    readonly env: ImportMetaEnv;
}
