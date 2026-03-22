import { create } from 'zustand'

interface UiState {
  activeCitationIndex: number | null
  sidebarOpen: boolean
  theme: 'dark' | 'light'

  setActiveCitation: (index: number | null) => void
  toggleSidebar: () => void
  setSidebarOpen: (open: boolean) => void
  setTheme: (theme: 'dark' | 'light') => void
}

export const useUiStore = create<UiState>()((set) => ({
  activeCitationIndex: null,
  sidebarOpen: true,
  theme: 'dark',

  setActiveCitation: (index) => set({ activeCitationIndex: index }),
  toggleSidebar: () => set((s) => ({ sidebarOpen: !s.sidebarOpen })),
  setSidebarOpen: (open) => set({ sidebarOpen: open }),
  setTheme: (theme) => set({ theme }),
}))
